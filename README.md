# Laboratorio 1 — Almacenamiento y validación de ficheros XML

**Asignatura:** Bases de Datos Avanzadas  
**Alumno:** Andrés Cramosr

## Descripción

Laboratorio sobre representación, validación y consulta de datos relacionales en formato XML. Se parte del esquema de ejemplo `HR` (Human Resources) de Oracle y se transforma a XML, se valida con XSD y se consulta con XQuery en BaseX y eXist-DB.

## Archivos SQL de origen

Ubicados en `data/db-sample-schemas-23.3/human_resources/`:

| Archivo | Descripción |
|---|---|
| `hr_create.sql` | DDL original de Oracle (con directivas SQL*Plus) |
| `hr_create.clean.sql` | DDL limpio — solo `CREATE TABLE`, `ALTER TABLE`, `CREATE SEQUENCE` |
| `hr_populate.sql` | Datos originales en bloques PL/SQL con `TO_DATE(...)` |
| `hr_populate.clean.sql` | INSERTs normalizados, uno por línea |

## Estructura de `data/db/`

```
data/db/
└── lab1/
    ├── data/
    │   └── hr_populate.xml          ← documento XML generado (215 registros)
    ├── schema/
    │   └── hr_schema.xsd            ← esquema de validación XSD
    ├── scripts/
    │   └── sql_to_xml.py            ← conversor SQL → XML
    └── queries/
        ├── count_departments.xq     ← empleados por departamento
        ├── count_departments.xml
        ├── employees_marketing_americas.xq   ← empleados de Marketing en Americas
        ├── employees_marketing_americas.xml
        ├── workers_per_region_location.xq    ← trabajadores por región y ubicación
        └── workers_per_region_location.xml
```
