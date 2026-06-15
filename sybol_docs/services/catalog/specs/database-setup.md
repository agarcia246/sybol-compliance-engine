# Database Setup Guide - Catalog v2

Scripts para configurar la base de datos catalog desde cero.

## 📋 Orden de Ejecución

### 1. **Eliminar BD existente** (si existe)

```bash
psql -h localhost -U root -f database/drop_database.sql
```

**⚠️ PRECAUCIÓN:** Este script elimina completamente la base de datos catalog y desconecta todos los usuarios.

### 2. **Crear usuario y BD**

```bash
psql -h localhost -U root -f database/setup_database.sql
```

Esto crea:
- Usuario: `catalog`
- Contraseña: `catalog` (DEV ONLY)
- Base de datos: `catalog`
- Permisos completos para el usuario catalog

### 3. **Inicializar schema**

```bash
psql -h localhost -U catalog -d catalog -f database/schema.sql
```

O usando el script init.sql:

```bash
psql -h localhost -U root -f database/init.sql
```

## 🔧 Scripts Disponibles

| Script | Descripción |
|--------|-------------|
| `drop_database.sql` | Elimina BD catalog y desconecta usuarios |
| `setup_database.sql` | Crea usuario catalog/catalog y BD catalog |
| `init.sql` | Inicializa extensiones y ejecuta schema.sql |
| `schema.sql` | Schema completo (tablas, índices, triggers, vistas) |
| `setup.sql` | Configuración de permisos (legacy) |

## 🚀 Setup Rápido (Fresh Install)

```bash
# En el directorio del proyecto catalog
cd database

# 1. Crear usuario y BD (como superusuario root/postgres)
psql -h localhost -U root < setup_database.sql

# 2. Crear schema (como usuario catalog)
psql -h localhost -U catalog -d catalog < schema.sql

# Verificar
psql -h localhost -U catalog -d catalog -c "\dt"
```

## 🔄 Reset Completo (Borrar y Recrear)

```bash
cd database

# 1. Eliminar todo
psql -h localhost -U root < drop_database.sql

# 2. Crear desde cero
psql -h localhost -U root < setup_database.sql

# 3. Inicializar schema
psql -h localhost -U catalog -d catalog < schema.sql
```

## 📊 Verificación

```bash
# Ver tablas creadas
psql -h localhost -U catalog -d catalog -c "\dt"

# Ver vistas
psql -h localhost -U catalog -d catalog -c "\dv"

# Ver permisos del usuario
psql -h localhost -U root -d catalog -c "\du catalog"

# Ver información de la BD
psql -h localhost -U root -c "\l catalog"
```

## 🔐 Credenciales por Entorno

### Development
- Usuario: `catalog`
- Contraseña: `catalog`
- Host: `localhost` o `172.19.1.100` (Docker)
- Puerto: `5432`
- Database: `catalog`

### Production
⚠️ **Usar AWS Secrets Manager** - No usar contraseñas hardcodeadas

## 📁 Estructura de Tablas

- `compliance_regions` - Regiones y jerarquías de compliance
- `compliance_region_children` - Relaciones jerárquicas
- `documents` - Documentos versionables (antes Origins)
- `document_versions` - Historial de versiones
- `claims` - Atributos/campos (antes Attributes)
- `forms` - Definiciones de formularios
- `form_sections` - Secciones dentro de formularios
- `form_fields` - Campos dentro de secciones

## 🛠️ Troubleshooting

**Error: "database catalog does not exist"**
```bash
# Ejecutar setup_database.sql primero
psql -h localhost -U root < database/setup_database.sql
```

**Error: "role catalog does not exist"**
```bash
# Recrear usuario
psql -h localhost -U root -c "CREATE USER catalog WITH PASSWORD 'catalog';"
```

**Error: "permission denied"**
```bash
# Dar permisos
psql -h localhost -U root -d catalog -c "GRANT ALL PRIVILEGES ON DATABASE catalog TO catalog;"
```

**Resetear contraseña**
```bash
psql -h localhost -U root -c "ALTER USER catalog WITH PASSWORD 'catalog';"
```
