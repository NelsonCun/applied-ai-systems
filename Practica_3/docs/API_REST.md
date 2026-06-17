# API REST

## Convenciones

- Base local: `http://localhost:8001/api/v1`
- Documentación Swagger: `http://localhost:8001/docs`
- Autenticación: `Authorization: Bearer <token>`
- Formato general: JSON, excepto cargas y descargas.

## Autenticación

| Método | Ruta | Descripción |
|---|---|---|
| POST | `/auth/login` | Iniciar sesión |
| GET | `/auth/me` | Consultar usuario autenticado |

Ejemplo:

```bash
curl -sS -X POST \
  http://localhost:8001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "identifier": "admin",
    "password": "Admin123*"
  }'
```

## Dashboard

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/dashboard/summary` | Métricas globales, por estado, proveedor y mes |

## Categorías

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/categories` | Listar categorías activas |

## Proveedores

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/providers` | Listar con paginación y filtros |
| POST | `/providers` | Crear |
| GET | `/providers/{id}` | Consultar |
| PUT | `/providers/{id}` | Actualizar |
| PATCH | `/providers/{id}/status` | Activar o desactivar |
| DELETE | `/providers/{id}` | Desactivar |

Filtros de listado:

- `page`
- `page_size`
- `search`
- `is_active`
- `category_id`

## Facturas

| Método | Ruta | Descripción |
|---|---|---|
| POST | `/invoices/upload` | Carga individual |
| POST | `/invoices/batch` | Carga de hasta 20 documentos |
| POST | `/invoices/{id}/process` | Procesar o reprocesar |
| GET | `/invoices` | Listar y filtrar |
| GET | `/invoices/{id}` | Consultar detalle |
| GET | `/invoices/{id}/ocr` | Consultar OCR |
| GET | `/invoices/{id}/logs` | Consultar bitácora |
| GET | `/invoices/{id}/file` | Documento original |
| GET | `/invoices/{id}/processed-file` | Imagen preprocesada |
| PUT | `/invoices/{id}/review` | Corregir y confirmar |

Filtros:

- `page`
- `page_size`
- `search`
- `status`
- `provider_id`

Carga individual:

```bash
curl -X POST \
  http://localhost:8001/api/v1/invoices/upload \
  -H "Authorization: Bearer ${TOKEN}" \
  -F "file=@factura.pdf"
```

Carga masiva:

```bash
curl -X POST \
  http://localhost:8001/api/v1/invoices/batch \
  -H "Authorization: Bearer ${TOKEN}" \
  -F "files=@factura_1.pdf" \
  -F "files=@factura_2.png"
```

## Reportes

| Método | Ruta | Descripción |
|---|---|---|
| POST | `/reports` | Solicitar generación |
| GET | `/reports` | Listar |
| GET | `/reports/{id}` | Consultar |
| GET | `/reports/{id}/download` | Descargar |

Ejemplo:

```json
{
  "report_type": "ADMINISTRATIVE",
  "format": "PDF",
  "date_from": null,
  "date_to": null,
  "provider_id": null,
  "status": "PROCESSED"
}
```

## Automatizaciones

| Método | Ruta | Descripción |
|---|---|---|
| POST | `/automations/rpa/invoices/{invoice_id}` | Encolar RPA |
| GET | `/automations/rpa` | Listar |
| GET | `/automations/rpa/{run_id}` | Consultar |
| GET | `/automations/rpa/{run_id}/evidence` | Descargar evidencia |

## Correos

| Método | Ruta | Descripción |
|---|---|---|
| POST | `/emails/reports/{report_id}` | Enviar reporte |
| GET | `/emails` | Historial |
| GET | `/emails/{email_id}` | Consultar envío |

Ejemplo:

```json
{
  "recipient": "auditoria@example.com",
  "subject": "Reporte SmartInvoice",
  "message": "Se adjunta el reporte solicitado."
}
```

## Salud

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/api/v1/health` | Comprueba PostgreSQL y Redis |

## Códigos frecuentes

| Código | Uso |
|---:|---|
| 200 | Consulta correcta |
| 201 | Recurso creado |
| 202 | Tarea encolada |
| 401 | Token ausente o inválido |
| 403 | Usuario inactivo o sin rol |
| 404 | Recurso inexistente |
| 409 | Conflicto de estado o duplicado |
| 422 | Validación fallida |
| 503 | Dependencia no disponible |
