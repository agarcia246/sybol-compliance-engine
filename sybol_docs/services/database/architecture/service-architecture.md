# Database Service — Architecture

## Propósito

Herramienta de administración de base de datos (Python) para verificar, auditar y corregir los permisos PostgreSQL en entornos multi-tenant. No es un servicio HTTP — es un toolset de operaciones para el equipo de infraestructura.

## Componentes

```
database/
├── check_permissions.py        ← Script principal de auditoría
├── apply_permissions.sh        ← Shell helper para aplicar correcciones
├── analyze_permissions.sh      ← Shell helper para análisis
├── permissions_policy.yaml     ← Política de permisos producción
├── permissions_policy_dev.yaml ← Política de permisos desarrollo
├── permissions_policy_staging.yaml ← Política staging
└── requirements.txt            ← Dependencias Python
```

## Flujo de auditoría

```
┌─────────────────────┐
│   PostgreSQL RDS    │  ← Extrae permisos actuales
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│ check_permissions.py│  ← Compara con política YAML
└──────────┬──────────┘
           ├─ output/reporte_permisos.xlsx   (visual Excel)
           ├─ output/compliance_report.txt   (texto)
           └─ output/fix_permissions.sql     (SQL correctivo)
```

## Políticas de permisos

Las políticas YAML definen para cada rol/tenant los permisos esperados sobre esquemas y tablas. El script detecta desviaciones y genera el SQL necesario para corregirlas.

## Uso

```bash
pip3 install -r requirements.txt
python3 check_permissions.py
# Revisar output/compliance_report.txt
# Aplicar correcciones: psql -f output/fix_permissions.sql
```

## Documentación relacionada

- [Business Rules](../specs/business-rules.md)
- [Permissions Diagram](../specs/permissions-diagram.md)
- [ADR-0003 global — Multi-tenant DB Design](../../global/decisions/0003-multi-tenant-database-design.md)
