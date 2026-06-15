# Sybol Catalog Service

API REST para gestión de catálogo de documentos, claims, formularios y regiones de compliance.

## 🏗 Arquitectura

- **Documents**: Contenedores conceptuales versionables (antes Origins)
- **Claims**: Definiciones reutilizables con validación regex (antes Attributes)
- **Forms**: Vistas lógicas sobre claims con secciones y campos
- **Compliance Regions**: Jerarquía de jurisdicciones y regiones regulatorias

## 🔐 Autenticación

### GET Endpoints
- **Sin Authorization header**: Acceso público con usuario por defecto de BD (connection pool)
- **Con Authorization Bearer token**: Autenticación con STS del tenant, acceso a BD catalog

### POST/DELETE Endpoints
- **Obligatorio Authorization Bearer token**: Solo tenant `sybol` puede realizar modificaciones
- Usa STS credentials del tenant sybol pero conecta a BD catalog

## 📋 Estructura del Proyecto

```
catalog/
├── src/
│   ├── config/           # Configuración centralizada
│   ├── controllers/      # Lógica HTTP
│   ├── middleware/       # Auth y validación
│   ├── routes/          # Definición de endpoints
│   ├── repositories/    # Acceso a datos
│   ├── validators/      # Schemas Joi
│   ├── persistence/     # Conexión dual-mode a BD
│   ├── lib/             # AWS utilities (STS, Secrets, KMS)
│   ├── utils/           # Helpers (logger, response, auth)
│   ├── app.js           # Express app
│   ├── server.js        # Servidor standalone
│   └── lambda.js        # Handler para Lambda
├── database/            # SQL schemas y setup
├── deploy/              # Scripts de despliegue
│   ├── start.sh         # Iniciar con docker-compose
│   └── docker-compose-files/
│       ├── catalog-compose.yaml
│       └── env/
│           └── dev.env
├── Dockerfile
├── .env.example         # Template de variables
├── package.json
└── README.md
```

## 🚀 Setup

### 1. Instalar Dependencias

```bash
npm install
```

### 2. Configurar Entorno

```bash
cp .env.example .env
# Editar .env con tus credenciales
```

**Variables Obligatorias:**
- `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`
- `AWS_REGION`, `AWS_ACCOUNT_ID`, `AWS_TENANT_ROLE_ARN`
- `AWS_SECRETS_REGION`, `AWS_SECRET_NAME_PREFIX`, `SYBOL_AWS_REGION`
- `COGNITO_USER_POOL_ID`, `COGNITO_REGION`

**Variables Opcionales:**
- `PORT`, `NODE_ENV`, `LOG_LEVEL`
- `DB_MAX_CONNECTIONS`, `DB_IDLE_TIMEOUT`, `DB_CONNECTION_TIMEOUT`
- `ALLOWED_ORIGINS`, `STS_CACHE_DURATION`

### 3. Crear Base de Datos

```bash
# Crear BD
createdb catalog

# Ejecutar schema
psql -h $DB_HOST -U $DB_USER -d catalog -f database/schema.sql

# Configurar permisos
psql -h $DB_HOST -U $DB_USER -d catalog -f database/setup.sql
```

### 4. Iniciar Servidor

**Desarrollo:**
```bash
npm run dev
```

**Producción:**
```bash
npm start
```

**Docker Compose:**
```bash
cd deploy
./start.sh -e dev
```

## 📡 Endpoints

### Documents
```
GET    /documents              # Público
GET    /documents/:id          # Público
GET    /documents/:id/versions # Público
POST   /documents              # Solo sybol
POST   /documents/:id          # Solo sybol
DELETE /documents/:id          # Solo sybol
```

### Claims
```
GET    /claims                 # Público
GET    /claims/:id             # Público
POST   /claims                 # Solo sybol
POST   /claims/:id             # Solo sybol
DELETE /claims/:id             # Solo sybol
```

### Forms
```
GET    /forms                  # Público
GET    /forms/:id              # Público
GET    /forms/:id/schema       # Público (schema completo)
POST   /forms                  # Solo sybol
POST   /forms/:id              # Solo sybol
DELETE /forms/:id              # Solo sybol
POST   /forms/:id/sections     # Solo sybol
POST   /forms/:id/sections/reorder # Solo sybol
POST   /forms/:id/sections/:sectionId # Solo sybol
DELETE /forms/:id/sections/:sectionId # Solo sybol
POST   /forms/:id/fields       # Solo sybol
POST   /forms/:id/fields/reorder # Solo sybol
```

### Fields
```
POST   /fields/:fieldId        # Solo sybol
DELETE /fields/:fieldId        # Solo sybol
```

### Compliance Regions
```
GET    /compliance-regions             # Público
GET    /compliance-regions/:id         # Público
GET    /compliance-regions/hierarchy   # Público (jerarquía completa)
POST   /compliance-regions             # Solo sybol
POST   /compliance-regions/:id         # Solo sybol
DELETE /compliance-regions/:id         # Solo sybol
```

## 🧪 Testing con Postman

Importar la colección `Catalog.postman_collection.json`:

1. Abrir Postman
2. Import → File → Seleccionar `Catalog.postman_collection.json`
3. Configurar variables:
   - `baseUrl`: http://localhost:3000 (o tu URL)
   - `idToken`: Tu token JWT de Cognito (para requests autenticados)

La colección incluye:
- ✅ Health check
- 📄 Todos los endpoints de Documents
- 🏷️ Todos los endpoints de Claims
- 📋 Todos los endpoints de Forms (con secciones y campos)
- 🗂️ Todos los endpoints de Fields
- 🌍 Todos los endpoints de Compliance Regions

## 🛠 Tecnologías

- **Runtime**: Node.js 18+
- **Framework**: Express
- **Database**: PostgreSQL con pg driver
- **Auth**: AWS Cognito (jose para JWT)
- **AWS**: STS, Secrets Manager, KMS
- **Validación**: Joi
- **Deployment**: Docker, Lambda (serverless-http)

## 🗄 Base de Datos

### Tablas Principales

- `documents` - Documentos con versionado
- `document_versions` - Historial de versiones
- `claims` - Atributos/campos de documentos
- `forms` - Definiciones de formularios
- `form_sections` - Secciones dentro de formularios
- `form_fields` - Campos dentro de secciones (vinculados a claims)
- `compliance_regions` - Regiones de compliance
- `compliance_region_children` - Relaciones jerárquicas

### Características

- ✅ Versionado de documentos (historial completo)
- ✅ Soft deletes (status: active/archived/deprecated)
- ✅ Validación regex en claims
- ✅ Jerarquía de compliance regions
- ✅ OR logic en form fields (or_group_id)
- ✅ Ordenamiento de secciones y campos
- ✅ Triggers automáticos para updated_at
- ✅ Vistas para queries complejas

## 🔧 Desarrollo

### Estructura de Código

- **Controllers**: Parsean request → llaman repositories → formatean response
- **Repositories**: Ejecutan queries → mapean rows → retornan datos
- **Middleware**: Autenticación (dual-mode) + validación (Joi)
- **Validators**: Schemas Joi para create/update de cada entidad

### Conexión Dual-Mode

```javascript
// Sin auth (público) → usa connection pool
// Con auth → usa STS credentials pero forzando database: 'catalog'

if (!authContext) {
  return pool.query(sql, params); // Pool estático
} else {
  const client = new Client({
    ...stsCredentials,
    database: 'catalog' // SIEMPRE catalog
  });
  // ... ejecuta query
}
```

### Añadir Nuevos Endpoints

1. Crear métodos en repository (`src/repositories/`)
2. Crear métodos en controller (`src/controllers/`)
3. Crear validators en (`src/validators/`)
4. Añadir routes en (`src/routes/`)
5. Aplicar middleware apropiado (auth + validation)

## 📦 Deployment

### Docker Local

```bash
cd deploy
./start.sh -e dev
```

### Lambda (Serverless)

El handler `src/lambda.js` está listo para deployment en AWS Lambda con API Gateway.

```yaml
# serverless.yml example
functions:
  catalog:
    handler: src/lambda.handler
    events:
      - http:
          path: /{proxy+}
          method: ANY
```

### ECS/EKS

Usar el Dockerfile multi-stage incluido:

```bash
docker build -t catalog:latest .
docker push your-registry/catalog:latest
```

## 🔒 Seguridad

- ✅ JWT validation con Cognito
- ✅ Tenant-based access control
- ✅ Solo sybol puede escribir
- ✅ Parameterized queries (SQL injection proof)
- ✅ Joi input validation
- ✅ Helmet security headers
- ✅ STS temporary credentials
- ✅ Secrets Manager para DB credentials
- ✅ PII marking en claims

## 📊 Monitoreo

**Health Check:**
```bash
curl http://localhost:3000/health
```

**Response:**
```json
{
  "status": "ok",
  "service": "catalog",
  "timestamp": "2026-02-11T10:30:00.000Z"
}
```

## 🐛 Troubleshooting

**Database connection fails:**
- Verificar variables DB_* en .env
- Comprobar security groups/firewall
- Verificar credenciales

**Authentication errors:**
- Verificar COGNITO_USER_POOL_ID
- Comprobar que el token no esté expirado
- Verificar header `Authorization: Bearer <token>`

**403 Forbidden en writes:**
- Solo tenant `sybol` puede escribir
- Verificar custom:tenant_id en el token JWT

## 📚 Documentación Adicional

- [database/schema.sql](database/schema.sql) - Schema completo de BD
- [Catalog.postman_collection.json](Catalog.postman_collection.json) - Colección Postman

## 🔄 Migración desde v1

**Cambios principales:**

| v1               | v2                  |
|------------------|---------------------|
| Origins          | Documents           |
| Attributes       | Claims              |
| Jurisdiction     | Compliance Path     |
| -                | Forms (nuevo)       |

**Pasos de migración:**
1. Exportar datos de v1
2. Transformar schema
3. Importar a v2
4. Actualizar clientes
5. Cutover gradual

---

**Version**: 2.0.0  
**Last Updated**: 2026-02-11  
**Maintainer**: Sybol Platform Team
