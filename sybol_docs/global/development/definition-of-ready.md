# EPIC 1 — Bulk Credential Issuance via File Upload

**Objetivo:** permitir la emisión masiva de credenciales verificables a partir de un fichero de carga.

## User Story 1.1 — Definir formato de fichero de carga

**Tipo:** Functional Definition  
**Estimación:** 1 día  
**Depende de:** nada

### Descripción

Como proveedor de certificados  
quiero un formato estándar de fichero para cargar certificados en bloque  
para emitir credenciales automáticamente en el sistema.

### Tasks

- Definir datos mínimos comunes para cualquier certificado
- Definir metadatos específicos por tipo de certificado
- Definir estructura del fichero (.xlsx)
- Definir mapeo de campos estándar

**Campos iniciales propuestos:**

- Fecha Inicio
- Fecha Fin
- CIF
- CUPS
- KWH/MWH
- Tecnología
- Origen
- Código
- Nombre
- Localización
- Fase
- DOCUMENTO_CATALOGO
- DID_SUBJECT

### Deliverables

- Documento de especificación del formato
- Ejemplo de fichero XLSX

## User Story 1.2 — Interfaz de carga de fichero

**Tipo:** Functional / UX  
**Estimación:** 2 días  
**Depende de:** Story 1.1

### Descripción

Como usuario del wallet  
quiero subir un fichero de certificados  
para procesar múltiples emisiones de credenciales en lote.

### Tasks

- Definir cómo acceder a la carga desde el wallet
- Diseñar modal/pantalla de carga
- Diseñar feedback durante procesamiento
- Diseñar notificación de resultado (OK / KO)
- Definir visualización de identidades DIDLESS
- Definir visualización de credenciales emitidas

### Deliverables

- Wireframes
- Flujo UX

## User Story 1.3 — Flujo DIDLESS (Subject inexistente)

**Tipo:** Functional / Identity Flow  
**Estimación:** 1 día  
**Depende de:** Story 1.1

### Descripción

Como sistema emisor  
quiero emitir credenciales incluso cuando el usuario aún no tiene DID  
para permitir que posteriormente el sujeto reclame la credencial.

### Tasks

- Definir estrategia de identificación posterior
- Evaluar opciones:

**Opciones posibles:**

- Password generado por proveedor
- Identificador único
- Challenge estilo OAuth
- Claim mediante email + challenge
- Claim mediante DID creation

- Definir flujo de reclamación

### Deliverables

- Diagrama de flujo DIDLESS
- Especificación de identificación posterior

# EPIC 2 — Backend Processing Pipeline

**Objetivo:** construir el pipeline técnico de ingestión, validación y emisión de credenciales.

## User Story 2.1 — Procesamiento de fichero de certificados

**Tipo:** Backend  
**Estimación:** 3 días  
**Depende de:** Epic 1

### Descripción

Como backend de credenciales  
quiero procesar ficheros de certificados  
para emitir credenciales o crear registros DIDLESS automáticamente.

### Tasks

- Crear endpoint para procesamiento de ficheros pesados
- Implementar validación de datos
- Diseñar mapeo XLSX → JSON
- Generar documentos de catálogo de credenciales
- Emitir VC cuando exista DID
- Crear credenciales DIDLESS cuando no exista

### Componentes

- File Processor
- Validation Layer
- Mapping Engine
- Credential Issuer
- Didless Storage

## User Story 2.2 — Reclamación de credenciales DIDLESS

**Tipo:** Backend / Identity  
**Estimación:** 2 días  
**Depende de:** Story 1.3

### Descripción

Como usuario final  
quiero reclamar una credencial emitida sin DID  
para asociarla a mi identidad digital.

### Tasks

- Implementar endpoint de identificación
- Resolver matching del sujeto
- Emitir VC final asociada al DID
- Marcar registro DIDLESS como reclamado

## User Story 2.3 — Consulta de datos y credenciales

**Tipo:** Backend API  
**Estimación:** 1 día

### Descripción

Como cliente del sistema  
quiero consultar credenciales y registros emitidos  
para integrar la información en otras aplicaciones.

### Tasks

- Definir tipos de consulta
- Definir filtros posibles

**Ejemplo:**

- CIF
- CUPS
- Technology
- Date range
- Credential status
- Issuer

- Implementar endpoint de consulta

# EPIC 3 — Blockchain Integration Layer

**Objetivo:** integrar el sistema con la capa blockchain.

**Estimación:** 10 días

Esta epic puede comenzar desde el inicio.

## User Story 3.1 — Módulo de conexión blockchain

### Tasks

- Implementar módulo de conexión blockchain
- Implementar recuperación de estado

## User Story 3.2 — Gestión de identidades

### Tasks

- Crear identidades DID
- Gestionar claves
- Integrar con wallet

## User Story 3.3 — Emisión de credenciales en blockchain

### Tasks

- Funcionalidad de emisión VC
- Registro en blockchain

## User Story 3.4 — Gestión de credenciales DIDLESS

### Tasks

- Emisión DIDLESS
- Registro temporal
- Preparación para claim

## User Story 3.5 — Claim de credenciales DIDLESS

### Tasks

- Resolver claim
- Asociar DID

## User Story 3.6 — Exposición API

### Tasks

- Conectar capas internas
- Exponer en API Gateway

## User Story 3.7 — Seguridad e infraestructura

### Tasks

- Configuración de roles
- Gestión de accesos
- Seguridad de infraestructura

# EPIC 4 — Integración final

**Estimación:** 2 días

## User Story — Integración end-to-end

### Tasks

- Integración frontend → backend
- Integración backend → blockchain
- Testing completo
- Ajustes de UX
- Documentación técnica

---

## Resultado final (estructura GitHub)

```text
EPIC 1
  US1.1 Formato fichero carga
  US1.2 Interfaz carga fichero
  US1.3 Flujo DIDLESS

EPIC 2
  US2.1 Procesamiento fichero
  US2.2 Reclamación credencial
  US2.3 Consulta datos

EPIC 3
  US3.1 Blockchain connection
  US3.2 Identity creation
  US3.3 Credential issuance
  US3.4 DIDLESS issuance
  US3.5 DIDLESS claim
  US3.6 API exposure
  US3.7 Security & infra

EPIC 4
  Integración final
```
