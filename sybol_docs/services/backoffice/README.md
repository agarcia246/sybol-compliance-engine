## Billing Endpoints

- `POST /api/bo/billing` — Guarda datos de facturación. Body: `{ userId, billingData }`
- `GET /api/bo/billing?userId=...` — Obtiene datos de facturación

# Sybol Backoffice API

Backend Node.js profesional para onboarding, autenticación, gestión de sesión, facturación y verificación KYB (Sumsub), desplegado en AWS Lambda con Docker y CI/CD.

**Base Path:** Todos los endpoints están bajo `/api/bo/*`

## Tabla de contenidos
- [Descripción](#descripción)
- [Estructura del proyecto](#estructura-del-proyecto)
- [Instalación y configuración local](#instalación-y-configuración-local)
- [Despliegue en AWS Lambda](#despliegue-en-aws-lambda)
- [Testing y calidad](#testing-y-calidad)
- [Endpoints principales](#endpoints-principales)
- [Documentación OpenAPI](#documentación-openapi)
- [Buenas prácticas](#buenas-prácticas)
- [Seguridad](#seguridad)
- [Contacto](#contacto)

## Descripción
Este repositorio implementa el backend para Sybol, cubriendo onboarding, login, gestión de sesión, facturación y verificación KYB. Utiliza Node.js, Express, AWS Cognito, PostgreSQL (RDS), Sumsub y despliegue serverless en Lambda vía Docker y ECR. Incluye CI/CD con GitHub Actions, linter, tests y documentación OpenAPI.

## Estructura del proyecto
```text
backoffice/
  src/
	 controllers/
	 helpers/
	 repositories/
	 services/
	 routes/
	 config/
	 bootstrap/
	 utils/
	 app.js
	 lambda.js
  test/
  db.sql
  Dockerfile
  .env.example
  .gitignore
  package.json
  eslint.config.js
  jest.config.js
  .github/workflows/deploy.yml
```

## Instalación y configuración local
1. Clona el repositorio y entra en la carpeta `backoffice`.
2. Copia `.env.example` a `.env` y rellena tus credenciales de RDS y Cognito.
3. Instala dependencias:
	```bash
	npm install
	npm install --save-dev jest supertest eslint
	```
4. Crea la base de datos en RDS y ejecuta el SQL de `db.sql`.
5. Ejecuta el backend en local:
	```bash
	npm run dev
	```
6. Ejecuta el linter y los tests:
	```bash
	npm run lint
	npm run test
	```

## Despliegue en AWS Lambda
1. Crea un repositorio en ECR para la imagen Docker.
2. Crea una función Lambda configurada para usar una imagen de ECR.
3. Configura los secrets en GitHub:
	- `AWS_ACCESS_KEY_ID`
	- `AWS_SECRET_ACCESS_KEY`
	- `AWS_REGION`
	- `ECR_REPOSITORY`
	- `AWS_ACCOUNT_ID`
	- `LAMBDA_FUNCTION_NAME`
4. Haz push a la rama principal (`feature/backoffice` o la que uses). El workflow compilará, subirá la imagen a ECR y actualizará Lambda automáticamente.

## Testing y calidad
- Linter: ESLint con reglas estrictas y autofix.
- Tests: Jest y Supertest para cobertura >90%.
- CI/CD: Workflows en `.github/workflows/deploy.yml` para test, build y despliegue.
- Logs: Logger centralizado en todos los endpoints y servicios.

## Endpoints principales

### Auth
- `POST /api/bo/auth` — Registro de usuario. Body: `{ email, password, name }`
- `POST /api/bo/auth/login` — Login. Body: `{ email, password }`
- `POST /api/bo/auth/refresh` — Refresco de sesión. Body: `{ refreshToken }`

### KYB (Sumsub)
- `POST /api/bo/kyb` — Genera token Sumsub para usuario. Body: `{ userId }`
- `GET /api/bo/kyb?userId=...` — Obtiene estado KYB. Respuesta: `{ status }`
- `POST /api/bo/kyb/webhook` — Recibe actualizaciones de estado desde Sumsub. Body: `{ userId, status }`

### Billing
- `POST /api/bo/billing` — Guarda datos de facturación. Body: `{ userId, billingData }`
- `GET /api/bo/billing?userId=...` — Obtiene datos de facturación

### Entity (async/sync)
- `POST /api/bo/entity?async=true` — Crear entidad de forma asíncrona. Devuelve `taskId` para consultar estado.
- `POST /api/bo/entity` — Crear entidad de forma síncrona. Devuelve entidad creada.
- `GET /api/bo/entity/task/:taskId` — Consultar estado y resultado de tarea asíncrona.

#### Ejemplo de uso async
```http
POST /api/bo/entity?async=true
{
  "entityId": "...",
  "alias": "...",
  "businessName": "..."
}
```
Respuesta:
```json
{
  "status": "pending",
  "taskId": "..."
}
```

#### Consultar estado de tarea
```http
GET /api/bo/entity/task/{taskId}
```
Respuesta:
```json
{
  "status": "completed",
  "result": { ... },
  "payload": { ... },
  "type": "entity.create",
  "taskId": "..."
}
```

- Todos los endpoints POST principales soportan modo asíncrono vía query param `async=true`. El endpoint `/entity/task/{taskId}` permite consultar el estado y resultado de la tarea.

## Documentación OpenAPI
La documentación completa de la API está en [`openapi.yaml`](./openapi.yaml), con endpoints agrupados por dominio (`auth`, `kyb`, `billing`) usando tags. Compatible con Swagger UI.

## Buenas prácticas
- Variables de entorno para credenciales y endpoints
- Código modular y desacoplado
- Linter y tests en cada PR
- No subir `.env` ni credenciales al repo
- Documentar endpoints y flujos
- Logs y trazabilidad en todos los servicios
- Cobertura de test >90%

## Seguridad
- Validación estricta de inputs y autenticación en todos los endpoints
- Protección de endpoints sensibles (webhook, billing)
- Nunca exponer secretos en el frontend
- Uso de HTTPS y políticas de CORS

## Contacto
Para dudas, soporte o contribuciones:
- [soporte@sybol.com](mailto:soporte@sybol.com)
- [Sybolid GitHub](https://github.com/Sybolid)
