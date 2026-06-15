# 🐳 Gestión de ECR Images para Lambda Functions

Este documento explica cómo gestionar las **imágenes Docker ECR** para las Lambda functions de Sybol, incluyendo cómo actualizar las funciones cuando hay nuevas imágenes.

## 🎯 Arquitectura ECR por entorno

### **Repositorios ECR:**
```
111891094335.dkr.ecr.eu-west-1.amazonaws.com/
├── dev/
│   ├── catalog:latest
│   ├── iom:latest
│   ├── svault:latest
│   └── bm:latest
└── pro/
    ├── catalog:latest
    ├── iom:latest
    ├── svault:latest
    └── bm:latest
```

### **Lambda Functions por entorno:**
```
Desarrollo (dev):
├── sybol-catalog-dev
├── sybol-iom-dev
├── sybol-svault-dev
└── sybol-bm-dev

Producción (pro):
├── sybol-catalog-pro
├── sybol-iom-pro
├── sybol-svault-pro
└── sybol-bm-pro
```

## 🚀 ¿Cómo actualizar Lambda Functions?

### **Opción 1: AWS CLI (Manual) - RECOMENDADO**

```bash
# 1. Actualizar imagen en ECR (desde directorio del servicio)
cd /path/to/catalog-service
./build-and-push.sh dev  # o 'pro'

# 2. Actualizar Lambda function para que use nueva imagen
aws lambda update-function-code \
  --function-name sybol-catalog-dev \
  --image-uri 111891094335.dkr.ecr.eu-west-1.amazonaws.com/dev/catalog:latest \
  --region eu-west-1

# 3. Verificar que se actualizó
aws lambda get-function \
  --function-name sybol-catalog-dev \
  --region eu-west-1 \
  --query 'Code.ImageUri'
```

### **Opción 2: Script automatizado**

```bash
#!/bin/bash
# update-lambda-image.sh

ENVIRONMENT="$1"  # dev o pro
SERVICE="$2"      # catalog, iom, svault, bm

if [ -z "$ENVIRONMENT" ] || [ -z "$SERVICE" ]; then
    echo "Uso: $0 <environment> <service>"
    echo "Ejemplo: $0 dev catalog"
    exit 1
fi

FUNCTION_NAME="sybol-${SERVICE}-${ENVIRONMENT}"
ECR_URI="111891094335.dkr.ecr.eu-west-1.amazonaws.com/${ENVIRONMENT}/${SERVICE}:latest"

echo "🔄 Actualizando Lambda: $FUNCTION_NAME"
echo "📦 Nueva imagen: $ECR_URI"

aws lambda update-function-code \
  --function-name "$FUNCTION_NAME" \
  --image-uri "$ECR_URI" \
  --region eu-west-1

echo "✅ Lambda actualizada exitosamente"
```

### **Opción 3: Re-despliegue completo CDK (Lento)**

```bash
# Solo usar si hay cambios en la configuración de la Lambda
cd CoreInfra
./deploy-sybol.sh dev  # o 'pro'
```

## ⚡ Workflow completo de desarrollo

### **1. Desarrollar nueva funcionalidad**
```bash
# Trabajar en el código del servicio
cd /path/to/catalog-service
# ... hacer cambios ...
```

### **2. Build y push nueva imagen**
```bash
# En el directorio del servicio
./build-and-push.sh dev

# Esto hace:
# - docker build -t catalog:latest .
# - docker tag catalog:latest 111891094335.dkr.ecr.eu-west-1.amazonaws.com/dev/catalog:latest
# - docker push 111891094335.dkr.ecr.eu-west-1.amazonaws.com/dev/catalog:latest
```

### **3. Actualizar Lambda (automático)**
```bash
# Script para actualizar todas las Lambdas del entorno
./update-all-lambdas.sh dev
```

### **4. Verificar despliegue**
```bash
# Probar endpoint
curl -X GET "https://api-gateway-url/catalog/health"

# Ver logs
aws logs tail /aws/lambda/sybol-catalog-dev --follow
```

## 🔄 Automatización con CI/CD

### **GitHub Actions ejemplo:**

```yaml
name: Deploy Lambda Service
on:
  push:
    paths:
      - 'services/catalog/**'
    branches:
      - main

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: eu-west-1
          
      - name: Login to Amazon ECR
        id: login-ecr
        uses: aws-actions/amazon-ecr-login@v1
        
      - name: Build and push Docker image
        working-directory: ./services/catalog
        run: |
          IMAGE_URI=111891094335.dkr.ecr.eu-west-1.amazonaws.com/dev/catalog:latest
          docker build -t catalog .
          docker tag catalog:latest $IMAGE_URI
          docker push $IMAGE_URI
          
      - name: Update Lambda function
        run: |
          aws lambda update-function-code \
            --function-name sybol-catalog-dev \
            --image-uri 111891094335.dkr.ecr.eu-west-1.amazonaws.com/dev/catalog:latest
```

## 📊 Comandos útiles

### **Ver información de Lambda:**
```bash
# Ver configuración actual
aws lambda get-function \
  --function-name sybol-catalog-dev \
  --region eu-west-1

# Ver variables de entorno
aws lambda get-function-configuration \
  --function-name sybol-catalog-dev \
  --region eu-west-1 \
  --query 'Environment.Variables'

# Ver imagen ECR actual
aws lambda get-function \
  --function-name sybol-catalog-dev \
  --region eu-west-1 \
  --query 'Code.ImageUri'
```

### **Listar todas las imágenes en ECR:**
```bash
# Ver imágenes en repositorio dev/catalog
aws ecr describe-images \
  --repository-name dev/catalog \
  --region eu-west-1

# Ver todas las Lambdas del entorno
aws lambda list-functions \
  --region eu-west-1 \
  --query 'Functions[?starts_with(FunctionName, `sybol-`)].{Name:FunctionName,Runtime:Runtime,Image:Code.ImageUri}'
```

### **Rollback a imagen anterior:**
```bash
# 1. Ver imágenes disponibles
aws ecr describe-images \
  --repository-name dev/catalog \
  --region eu-west-1 \
  --query 'imageDetails[*].{digest:imageDigest,tags:imageTags,pushed:imagePushedAt}' \
  --output table

# 2. Actualizar a imagen específica por digest
aws lambda update-function-code \
  --function-name sybol-catalog-dev \
  --image-uri 111891094335.dkr.ecr.eu-west-1.amazonaws.com/dev/catalog@sha256:abcd1234... \
  --region eu-west-1
```

## 🚨 Troubleshooting

### **Error: "The image manifest or layer media type is not supported"**
```bash
# Verificar que la imagen sea compatible con Lambda
docker inspect 111891094335.dkr.ecr.eu-west-1.amazonaws.com/dev/catalog:latest
```

### **Error: "Lambda function not found"**
```bash
# Verificar que la Lambda existe
aws lambda get-function --function-name sybol-catalog-dev --region eu-west-1
```

### **Error: "AccessDenied" al actualizar Lambda**
```bash
# Verificar permisos IAM para lambda:UpdateFunctionCode
aws iam simulate-principal-policy \
  --policy-source-arn arn:aws:iam::111891094335:user/your-user \
  --action-names lambda:UpdateFunctionCode \
  --resource-arns arn:aws:lambda:eu-west-1:111891094335:function:sybol-catalog-dev
```

### **Función no se actualiza inmediatamente**
```bash
# Forzar actualización con nuevo publish
aws lambda update-function-code \
  --function-name sybol-catalog-dev \
  --image-uri 111891094335.dkr.ecr.eu-west-1.amazonaws.com/dev/catalog:latest \
  --publish \
  --region eu-west-1
```

## 📈 Monitoreo y logs

### **Ver logs en tiempo real:**
```bash
# Seguir logs de una Lambda
aws logs tail /aws/lambda/sybol-catalog-dev --follow --region eu-west-1

# Ver errores específicos
aws logs filter-log-events \
  --log-group-name /aws/lambda/sybol-catalog-dev \
  --filter-pattern "ERROR" \
  --start-time $(date -d '1 hour ago' +%s)000 \
  --region eu-west-1
```

### **Métricas de desempeño:**
```bash
# Ver métricas de invocación
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Invocations \
  --dimensions Name=FunctionName,Value=sybol-catalog-dev \
  --start-time $(date -d '1 hour ago' --iso-8601) \
  --end-time $(date --iso-8601) \
  --period 300 \
  --statistics Sum \
  --region eu-west-1
```

## 💡 Mejores prácticas

1. **🏷️ Tagging de imágenes:** Usa tags semánticos como `v1.0.0`, no solo `latest`
2. **🔄 Testing:** Siempre prueba en `dev` antes de desplegar a `pro`  
3. **📝 Logs:** Incluye información de versión en logs de la aplicación
4. **⚡ Rollback:** Ten un plan de rollback para producción
5. **🚨 Monitoreo:** Configura alertas para errores post-despliegue

**Con esta arquitectura, actualizar Lambdas es tan simple como hacer push de una nueva imagen ECR y ejecutar un comando AWS CLI!** 🚀