# Diagrama entidad-relación — SmartInvoice

## 1. Descripción

El modelo relacional centraliza la información administrativa obtenida del procesamiento documental. La entidad principal es `invoices`, relacionada con usuarios, proveedores, categorías, bitácoras, reportes indirectos y ejecuciones RPA.

![Diagrama entidad-relación](./diagramas/Diagrama_ER.png)

## 2. Entidades principales

| Entidad | Propósito |
|---|---|
| `users` | Usuarios administrativos, credenciales, rol y estado. |
| `invoice_categories` | Clasificación de proveedores y facturas. |
| `providers` | Información de proveedores y NIT. |
| `invoices` | Documento, datos OCR, montos, estado y trazabilidad principal. |
| `processing_logs` | Eventos de carga, CV, OCR, extracción, validación y almacenamiento. |
| `invoice_items` | Estructura preparada para líneas de detalle. |
| `reports` | Reportes generados, filtros, archivo y estado. |
| `email_logs` | Envíos SMTP relacionados con reportes. |
| `automation_runs` | Ejecuciones RPA, resultado y evidencia. |

## 3. Relaciones

- Un usuario crea muchas facturas.
- Un usuario puede confirmar muchas facturas.
- Una categoría clasifica proveedores y facturas.
- Un proveedor puede asociarse con muchas facturas.
- Una factura puede tener muchas bitácoras y líneas de detalle.
- Una factura puede tener muchas ejecuciones RPA.
- Un usuario puede generar muchos reportes.
- Un reporte puede originar muchos envíos de correo.
- Una factura duplicada puede referenciar otra factura.

## 4. Integridad

El esquema utiliza claves foráneas, restricciones `CHECK`, tipos enumerados, índices únicos parciales y JSONB. La huella SHA-256 evita duplicados físicos y la combinación proveedor–número evita duplicados lógicos entre facturas válidas.

## 5. Estructuras de extensión

El esquema también contiene `scheduled_tasks`, `system_settings` y `external_api_logs`. Estas tablas preparan futuras funciones de programación, configuración persistente y auditoría de servicios externos, pero no constituyen módulos completos de la versión entregada.
