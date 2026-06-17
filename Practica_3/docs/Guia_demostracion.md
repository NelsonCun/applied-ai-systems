# Guía para la demostración presencial

## Objetivo

Demostrar el flujo completo de una factura desde la carga hasta el reporte final, incluyendo OCR, bitácora, RPA y correo.

## Preparación

```bash
docker compose up -d
docker compose ps
curl -s http://localhost:8001/api/v1/health | python3 -m json.tool
```

Abra previamente:

- Frontend: `http://localhost:5174`
- Swagger: `http://localhost:8001/docs`
- MailHog: `http://localhost:8025`
- RPA target: `http://localhost:8082`

## Guion sugerido

### 1. Arquitectura — 1 minuto

Explique:

- frontend React;
- API FastAPI;
- PostgreSQL;
- Redis y Celery;
- OpenCV y Tesseract;
- Playwright;
- SMTP;
- Docker Compose.

### 2. Inicio de sesión — 30 segundos

Ingrese con el usuario administrador y muestre la sesión JWT.

### 3. Proveedores — 1 minuto

Muestre el CRUD, validación de NIT y clasificación por categoría.

### 4. Carga de factura — 2 minutos

Use una factura nueva, no un archivo ya cargado.

1. Cargue el documento.
2. Muestre estado pendiente/procesando.
3. Explique que la API encoló una tarea Celery.
4. Espere el estado final.

### 5. OCR y Computer Vision — 2 minutos

Abra el detalle y muestre:

- original;
- imagen preprocesada;
- texto OCR;
- confianza;
- campos extraídos;
- proveedor asociado.

Explique redimensionado, deskew, denoising, binarización y Tesseract.

### 6. Validaciones y bitácora — 1 minuto

Muestre las etapas:

- UPLOAD;
- COMPUTER_VISION;
- OCR;
- EXTRACTION;
- VALIDATION.

Mencione validación de fecha, NIT, montos, confianza y duplicados.

### 7. Reporte — 1 minuto

Genere un reporte PDF administrativo, espere `SUCCESS` y descárguelo.

### 8. RPA — 2 minutos

Seleccione la factura procesada, ejecute la automatización y muestre:

- estado;
- ID externo;
- URL final;
- evidencia PNG.

Explique que Playwright inicia sesión y llena el formulario sin intervención humana.

### 9. Correo — 1 minuto

Envíe el reporte a `evaluacion@example.com`, abra el historial y después MailHog. Muestre el adjunto.

### 10. Volumen — 1 minuto

Muestre el lote `samples/batch_20` y el resultado:

```bash
python3 scripts/upload_verify_batch_20.py \
  --directory samples/batch_20 \
  --base-url http://localhost:8001 \
  --identifier admin \
  --password 'Admin123*' \
  --skip-upload
```

Resultado esperado:

```text
PROCESSED: 20
RESULTADO: CORRECTO
```

## Preguntas de defensa

### ¿Por qué Celery?

Porque OCR, RPA y reportes son operaciones lentas. La cola evita bloquear la API.

### ¿Dónde está la IA?

En el procesamiento inteligente del documento: Computer Vision, OCR, extracción estructurada, asociación difusa de proveedor y validación automática.

### ¿Cómo detecta duplicados?

Por SHA-256 del archivo y por proveedor+número de factura.

### ¿Qué ocurre con un OCR incorrecto?

La factura queda rechazada con errores visibles y puede revisarse manualmente.

### ¿La RPA usa API?

No. La RPA manipula un formulario web mediante navegador, que es la característica demostrativa del proceso robótico.

### ¿Los correos son reales?

La aplicación usa SMTP real. En desarrollo el destino es MailHog para evitar envíos externos.

### ¿Cómo se protege el sistema?

JWT, bcrypt, validación de archivos, roles, restricciones SQL y secretos mediante variables de entorno.

## Plan de contingencia

- Mantenga capturas de RPA existentes.
- Tenga reportes generados previamente.
- No elimine volúmenes antes de evaluar.
- Use un lote nuevo si debe demostrar carga.
- Verifique puertos y servicios 15 minutos antes.
- Mantenga una terminal con `docker compose logs -f worker`.
