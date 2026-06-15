# 🔑 KMS Key Management via Lambda Endpoints

Este documento explica cómo gestionar claves KMS dinámicamente usando endpoints Lambda, con diferenciación de permisos entre Admin y User roles.

## 🆕 **NUEVO: Flujo de KMS con Key IDs Específicos**

### **Cambio de Arquitectura (Noviembre 2025)**

**Antes:** Se usaban alias basados en tenant: `alias/tenant/{tenantId}/{role}-jwt`

**Ahora:** Se usan **Key IDs específicos** almacenados en DID Documents para máxima seguridad:

1. **Creación de clave KMS** → Genera Key ID único
2. **Actualización de DID Document** → Se añade Key ID al `verificationMethod`
3. **Firma JWT** → Se valida DID ownership + se extrae Key ID + se firma con KMS
4. **Validación de permisos** → STS AssumeRole valida acceso automáticamente

### **Ventajas del nuevo flujo:**
- ✅ **Seguridad granular**: Cada DID puede tener su propia clave KMS
- ✅ **Validación automática**: STS rechaza automáticamente accesos no autorizados
- ✅ **Trazabilidad**: Logs detallados de qué usuario usa qué clave
- ✅ **Flexibilidad**: Múltiples claves por tenant si es necesario

## 🎯 Arquitectura de KMS Management

### **Admin Role:**
- ✅ Puede crear claves KMS vía `POST /kms/create-key`
- ✅ Puede listar sus claves vía `GET /kms/list-keys`
- ✅ Puede usar todas las operaciones de cifrado
- ✅ Puede gestionar grants y permisos

### **User Role:**
- ❌ NO puede crear claves
- ✅ Puede usar claves existentes para cifrado/descifrado
- ✅ Puede listar claves (solo las de su tenant)
- ❌ NO puede gestionar grants

## 🐍 Ejemplo de Lambda para crear KMS Keys

```javascript
// CoreInfra/services/kmsManager/src/index.js
import { KMSClient, CreateKeyCommand, CreateAliasCommand, TagResourceCommand } from '@aws-sdk/client-kms';
import { getTenantStsSession } from '@sybol/tenant-sts-credentials';

export const handler = async (event) => {
  try {
    // 1. Obtener credenciales del tenant desde JWT
    const accessToken = event.headers.authorization?.replace('Bearer ', '');
    const credentials = await getTenantStsSession({ accessToken });
    
    const { tenantId, role, roleArn } = credentials;
    
    // 2. VERIFICAR PERMISOS - Solo Admin puede crear claves
    if (role !== 'admin') {
      return {
        statusCode: 403,
        body: JSON.stringify({
          error: 'Forbidden',
          message: 'Solo usuarios Admin pueden crear claves KMS',
          yourRole: role,
          requiredRole: 'admin'
        })
      };
    }
    
    // 3. Parsear request body
    const { keyUsage = 'ENCRYPT_DECRYPT', description } = JSON.parse(event.body);
    
    // 4. Usar credenciales del tenant para crear la clave
    const kms = new KMSClient({ 
      credentials,
      region: process.env.AWS_REGION 
    });
    
    // 5. Crear KMS Key con tags del tenant
    const createKeyResult = await kms.send(new CreateKeyCommand({
      Description: description || `KMS Key para tenant ${tenantId}`,
      KeyUsage: keyUsage,
      KeySpec: 'SYMMETRIC_DEFAULT',
      Origin: 'AWS_KMS',
      Tags: [
        { TagKey: 'tenantId', TagValue: tenantId },
        { TagKey: 'createdBy', TagValue: roleArn },
        { TagKey: 'environment', TagValue: 'production' },
        { TagKey: 'project', TagValue: 'sybol' }
      ]
    }));
    
    const keyId = createKeyResult.KeyMetadata.KeyId;
    
    // 6. Crear alias único para el tenant
    const keyName = `key-${Date.now()}`;
    const aliasName = `alias/sybol-tenant-${tenantId}-${keyName}`;
    
    await kms.send(new CreateAliasCommand({
      AliasName: aliasName,
      TargetKeyId: keyId
    }));
    
    // 7. Respuesta con información de la clave creada
    return {
      statusCode: 201,
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*'
      },
      body: JSON.stringify({
        message: 'KMS Key creada exitosamente',
        keyInfo: {
          keyId: keyId,
          keyArn: createKeyResult.KeyMetadata.Arn,
          aliasName: aliasName,
          tenantId: tenantId,
          createdBy: role,
          description: createKeyResult.KeyMetadata.Description
        },
        usage: {
          encrypt: `Usar alias: ${aliasName}`,
          exampleCommand: `aws kms encrypt --key-id ${aliasName} --plaintext "mi datos"`
        }
      })
    };
    
  } catch (error) {
    console.error('Error creating KMS key:', error);
    
    return {
      statusCode: 500,
      body: JSON.stringify({
        error: 'InternalServerError',
        message: 'Error al crear la clave KMS',
        details: error.message
      })
    };
  }
};
```

## 🔍 Ejemplo de Lambda para listar KMS Keys

```javascript
// CoreInfra/services/kmsManager/src/list-keys.js
import { KMSClient, ListKeysCommand, ListAliasesCommand, DescribeKeyCommand } from '@aws-sdk/client-kms';
import { getTenantStsSession } from '@sybol/tenant-sts-credentials';

export const handler = async (event) => {
  try {
    // 1. Obtener credenciales del tenant
    const accessToken = event.headers.authorization?.replace('Bearer ', '');
    const credentials = await getTenantStsSession({ accessToken });
    
    const { tenantId, role } = credentials;
    
    // 2. Usar credenciales del tenant
    const kms = new KMSClient({ 
      credentials,
      region: process.env.AWS_REGION 
    });
    
    // 3. Listar aliases del tenant
    const aliasesResult = await kms.send(new ListAliasesCommand({}));
    
    // 4. Filtrar solo aliases de su tenant
    const tenantAliases = aliasesResult.Aliases.filter(alias => 
      alias.AliasName?.startsWith(`alias/sybol-tenant-${tenantId}`)
    );
    
    // 5. Obtener detalles de cada clave
    const keyDetails = await Promise.all(
      tenantAliases.map(async (alias) => {
        try {
          const keyInfo = await kms.send(new DescribeKeyCommand({
            KeyId: alias.TargetKeyId
          }));
          
          return {
            aliasName: alias.AliasName,
            keyId: keyInfo.KeyMetadata.KeyId,
            keyArn: keyInfo.KeyMetadata.Arn,
            keyState: keyInfo.KeyMetadata.KeyState,
            keyUsage: keyInfo.KeyMetadata.KeyUsage,
            description: keyInfo.KeyMetadata.Description,
            creationDate: keyInfo.KeyMetadata.CreationDate
          };
        } catch (error) {
          console.warn(`Error getting key details for ${alias.AliasName}:`, error.message);
          return null;
        }
      })
    );
    
    // 6. Filtrar claves válidas
    const validKeys = keyDetails.filter(key => key !== null);
    
    return {
      statusCode: 200,
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*'
      },
      body: JSON.stringify({
        tenantId: tenantId,
        userRole: role,
        keysCount: validKeys.length,
        keys: validKeys,
        permissions: {
          canCreateKeys: role === 'admin',
          canUseKeys: true,
          canManageGrants: role === 'admin'
        }
      })
    };
    
  } catch (error) {
    console.error('Error listing KMS keys:', error);
    
    return {
      statusCode: 500,
      body: JSON.stringify({
        error: 'InternalServerError',
        message: 'Error al listar claves KMS',
        details: error.message
      })
    };
  }
};
```

## 🚀 Endpoints en API Gateway

En tu `CoreInfra`, los endpoints serían:

```typescript
// Agregar a tu HTTP API Gateway en CoreInfra
const kmsCreateRoute = httpApi.addRoutes({
  path: '/kms/create-key',
  methods: [HttpMethod.POST],
  integration: new HttpLambdaIntegration('KmsCreateIntegration', kmsCreateLambda),
  authorizer: jwtAuthorizer  // Requiere JWT válido
});

const kmsListRoute = httpApi.addRoutes({
  path: '/kms/list-keys',
  methods: [HttpMethod.GET], 
  integration: new HttpLambdaIntegration('KmsListIntegration', kmsListLambda),
  authorizer: jwtAuthorizer
});

const kmsEncryptRoute = httpApi.addRoutes({
  path: '/kms/encrypt',
  methods: [HttpMethod.POST],
  integration: new HttpLambdaIntegration('KmsEncryptIntegration', kmsEncryptLambda),
  authorizer: jwtAuthorizer
});
```

## 🎯 Uso desde el Frontend

```javascript
// Frontend - Crear clave (solo Admin)
const createKmsKey = async (description) => {
  const response = await fetch('/api/kms/create-key', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${jwtToken}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      description: `Clave para ${description}`,
      keyUsage: 'ENCRYPT_DECRYPT'
    })
  });
  
  if (response.status === 403) {
    alert('Solo usuarios Admin pueden crear claves KMS');
    return null;
  }
  
  return await response.json();
};

// Frontend - Listar claves (Admin y User)
const listKmsKeys = async () => {
  const response = await fetch('/api/kms/list-keys', {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${jwtToken}`
    }
  });
  
  return await response.json();
};

// Frontend - Cifrar datos (Admin y User)
const encryptData = async (keyAlias, plaintext) => {
  const response = await fetch('/api/kms/encrypt', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${jwtToken}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      keyId: keyAlias,  // ej: "alias/sybol-tenant-empresa-a-key-123456"
      plaintext: plaintext
    })
  });
  
  return await response.json();
};
```

## 📊 Diferencias de permisos por rol

| Operación | Admin Role | User Role |
|-----------|------------|-----------|
| `kms:CreateKey` | ✅ SÍ | ❌ NO |
| `kms:CreateAlias` | ✅ SÍ | ❌ NO |
| `kms:Encrypt` | ✅ SÍ | ✅ SÍ |
| `kms:Decrypt` | ✅ SÍ | ✅ SÍ |
| `kms:ListKeys` | ✅ SÍ | ✅ SÍ (filtrado) |
| `kms:DescribeKey` | ✅ SÍ | ✅ SÍ |
| `kms:CreateGrant` | ✅ SÍ | ❌ NO |
| `kms:RevokeGrant` | ✅ SÍ | ❌ NO |

## � **FLUJO COMPLETO: Creación y Uso de Claves KMS**

### **Paso 1: Crear clave KMS (solo Admin)**
```bash
POST /kms/create-key
Authorization: Bearer {jwt-admin-token}
Content-Type: application/json

{
  "keyUsage": "ENCRYPT_DECRYPT", 
  "description": "Clave para DID did:sybol:12345",
  "didId": "did:sybol:12345"  # Opcional: para vincular automáticamente
}
```

**Respuesta:**
```json
{
  "success": true,
  "keyId": "a1b2c3d4-e5f6-7890-abcd-123456789012",
  "alias": "alias/tenant/repsol/admin-jwt-12345",
  "arn": "arn:aws:kms:eu-west-1:111891094335:key/a1b2c3d4-e5f6-7890-abcd-123456789012"
}
```

### **Paso 2: Actualizar DID Document con KMS Key ID**
```bash
PUT /api/did-document/did:sybol:12345
Authorization: Bearer {jwt-admin-token}
Content-Type: application/json

{
  "document": {
    "verificationMethod": [
      {
        "id": "did:sybol:12345#key-1",
        "type": "Ed25519VerificationKey2020", 
        "controller": "did:sybol:12345",
        "kmsKeyId": "a1b2c3d4-e5f6-7890-abcd-123456789012"
      }
    ]
  }
}
```

### **Paso 3: Usar clave para firmar JWT**
Cuando se genera un credential con `issuer: "did:sybol:12345#key-1"`:

1. **Validación DID**: Se verifica que el DID existe y pertenece al tenant
2. **Extracción Key ID**: Se obtiene `kmsKeyId` del verification method
3. **Firma KMS**: Se usa el Key ID específico para firmar
4. **Validación automática**: STS rechaza si no hay permisos

```bash
POST /api/credentials
Authorization: Bearer {jwt-token}
Content-Type: application/json

{
  "issuer": "did:sybol:12345#key-1",  # DID + Key ID
  "recipient": "did:sybol:67890", 
  "claims": { "name": "John Doe" }
}
```

**El sistema automáticamente:**
- ✅ Valida que `did:sybol:12345` pertenece al tenant del JWT
- ✅ Extrae `kmsKeyId: a1b2c3d4-e5f6...` del verification method
- ✅ Firma con KMS usando ese Key ID específico
- ❌ **FALLA** si el usuario no tiene permisos para esa clave

## �🔐 Tags para aislamiento

Todas las claves creadas tienen tags automáticos:
```json
{
  "tenantId": "empresa-a",
  "createdBy": "arn:aws:iam::123456789:role/Sybol-empresa-a-Admin", 
  "environment": "production",
  "project": "sybol"
}
```

Y las políticas IAM verifican estos tags para aislamiento:
```typescript
conditions: {
  'StringEquals': {
    'aws:ResourceTag/tenantId': '${aws:PrincipalTag/tenantId}'
  }
}
```

De esta forma, **cada tenant solo puede crear/usar claves que tengan su `tenantId` en los tags**.