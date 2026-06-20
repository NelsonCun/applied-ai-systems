# Requerimientos de SmartInvoice

## 1. Alcance

SmartInvoice automatiza el procesamiento de facturas digitales desde su carga hasta el registro, consulta, generación de reportes, automatización RPA y notificación por correo.

## 2. Actores

| Actor | Responsabilidad |
|---|---|
| Administrador | Accede a todas las funciones administrativas y gestiona proveedores. |
| Operador | Consulta y procesa documentos según los permisos de autenticación disponibles. |
| Worker Celery | Ejecuta OCR, reportes, correos y RPA en segundo plano. |
| Sistema externo simulado | Recibe datos ingresados por la automatización Playwright. |
| Servidor SMTP | Recibe los mensajes y archivos adjuntos generados por la aplicación. |

## 3. Requerimientos funcionales

| ID | Requerimiento | Implementación | Estado |
|---|---|---|---|
| RF-01 | El sistema debe permitir iniciar sesión mediante usuario o correo y contraseña. | JWT, bcrypt y rutas `/auth/login` y `/auth/me`. | Cumplido |
| RF-02 | El sistema debe restringir las pantallas y endpoints administrativos a usuarios autenticados. | `ProtectedRoute`, interceptor Axios y dependencia `get_current_user`. | Cumplido |
| RF-03 | El administrador debe crear, consultar, actualizar, activar y desactivar proveedores. | CRUD `/providers`. | Cumplido |
| RF-04 | El sistema debe listar categorías activas para clasificar proveedores y facturas. | Endpoint `/categories`. | Cumplido |
| RF-05 | El usuario debe cargar una factura individual. | `POST /invoices/upload`. | Cumplido |
| RF-06 | El usuario debe cargar hasta 20 facturas en una operación. | `POST /invoices/batch`. | Cumplido |
| RF-07 | El sistema debe aceptar PDF, JPG, JPEG y PNG. | Validación por extensión y firma binaria. | Cumplido |
| RF-08 | El sistema debe rechazar archivos vacíos, incompatibles o mayores al límite configurado. | Servicio de carga y `MAX_UPLOAD_SIZE_MB`. | Cumplido |
| RF-09 | El sistema debe procesar cada documento con técnicas de Computer Vision. | Conversión, redimensionado, escala de grises, deskew, denoising, umbral adaptativo y morfología. | Cumplido |
| RF-10 | El sistema debe extraer texto mediante OCR local. | Tesseract y Pytesseract. | Cumplido |
| RF-11 | El sistema debe extraer número, fecha, proveedor, NIT, subtotal, impuestos y total. | Parser basado en expresiones regulares y normalización. | Cumplido |
| RF-12 | El sistema debe asociar automáticamente el proveedor. | Coincidencia exacta por NIT y coincidencia difusa por nombre. | Cumplido |
| RF-13 | El sistema debe validar fecha, NIT, montos y confianza OCR. | Validadores del parser y servicio de revisión. | Cumplido |
| RF-14 | El sistema debe almacenar resultados, texto OCR y metadatos. | PostgreSQL y campos JSONB. | Cumplido |
| RF-15 | El usuario debe consultar, buscar y filtrar facturas. | Listado paginado con filtros de estado, proveedor y texto. | Cumplido |
| RF-16 | El usuario debe visualizar el documento original y la imagen preprocesada. | Endpoints `/file` y `/processed-file`. | Cumplido |
| RF-17 | El usuario debe consultar el resultado OCR y la bitácora de una factura. | Endpoints `/ocr` y `/logs`. | Cumplido |
| RF-18 | El usuario debe corregir y confirmar manualmente datos rechazados. | `PUT /invoices/{id}/review`. | Cumplido |
| RF-19 | El sistema debe detectar documentos duplicados. | SHA-256 y validación lógica proveedor+número. | Cumplido |
| RF-20 | El sistema debe mostrar métricas administrativas. | Dashboard por estado, proveedor, mes, totales y confianza. | Cumplido |
| RF-21 | El sistema debe generar reportes administrativos. | PDF, XLSX y CSV con filtros. | Cumplido |
| RF-22 | El usuario debe descargar reportes generados. | `/reports/{id}/download`. | Cumplido |
| RF-23 | El sistema debe registrar facturas en un formulario externo mediante RPA. | Playwright y Chromium. | Cumplido |
| RF-24 | El sistema debe almacenar estado, resultado y evidencia de la RPA. | `automation_runs` y capturas PNG. | Cumplido |
| RF-25 | El sistema debe enviar reportes por correo. | SMTP asíncrono autenticado, STARTTLS, archivo adjunto y entrega real validada. | Cumplido |
| RF-26 | El usuario debe consultar el historial de correos. | Endpoints y pantalla de correos. | Cumplido |
| RF-27 | El sistema debe mantener una bitácora por etapa. | `processing_logs`: UPLOAD, COMPUTER_VISION, OCR, EXTRACTION y VALIDATION. | Cumplido |
| RF-28 | El procesamiento pesado debe ejecutarse en segundo plano. | Celery con Redis. | Cumplido |
| RF-29 | El sistema debe poder procesar al menos 20 facturas de prueba. | Lote `L20A`, resultado 20/20. | Cumplido |
| RF-30 | El sistema debe poder ejecutarse mediante Docker Compose. | Siete servicios orquestados. | Cumplido |
| RF-31 | El sistema debe estar disponible mediante una URL pública durante la evaluación. | Despliegue AWS EC2 accesible mediante IPv4 pública. | Cumplido |
| RF-32 | El sistema debe permitir administrar usuarios. | Existe modelo, autenticación y roles; no existe CRUD de usuarios en la interfaz. | Parcial |

## 4. Reglas de negocio

1. Un archivo no puede superar 15 MB por defecto.
2. Una carga masiva admite como máximo 20 archivos.
3. La extensión declarada debe coincidir con la firma binaria.
4. Una factura duplicada no puede reprocesarse ni confirmarse.
5. Solo las facturas `PROCESSED` pueden enviarse a la automatización RPA.
6. Solo los reportes `SUCCESS` pueden descargarse o enviarse por correo.
7. La fecha de factura no puede estar en el futuro.
8. El subtotal, impuesto y total no pueden ser negativos.
9. La diferencia entre `subtotal + impuesto` y `total` no puede superar Q0.10.
10. El NIT debe ser `CF`, nueve dígitos o formato histórico con guion.
11. El NIT de una revisión manual debe coincidir con el proveedor.
12. Una factura original se identifica físicamente por SHA-256.
13. Una factura lógica se identifica por proveedor y número de factura.
14. La confianza OCR mínima se configura mediante `OCR_MIN_CONFIDENCE`.
15. Los PDF se procesan hasta el límite configurado en `MAX_PDF_PAGES`.

## 5. Requerimientos no funcionales

| ID | Categoría | Requerimiento | Implementación o criterio |
|---|---|---|---|
| RNF-01 | Rendimiento | La API no debe bloquearse durante OCR, reportes, correo o RPA. | Celery y Redis desacoplan las tareas pesadas. |
| RNF-02 | Capacidad | La aplicación debe aceptar un lote de 20 facturas. | Límite implementado y validado 20/20. |
| RNF-03 | Disponibilidad | Los servicios críticos deben exponer verificaciones de salud. | Healthchecks de PostgreSQL, Redis, backend y RPA target. |
| RNF-04 | Integridad | Los datos monetarios y de NIT deben validarse antes de confirmarse. | Validaciones de backend y restricciones SQL. |
| RNF-05 | Integridad | No debe registrarse dos veces el mismo documento original. | Índice único parcial por SHA-256. |
| RNF-06 | Integridad | No debe existir más de una factura válida con igual proveedor y número. | Índice único parcial y detección previa. |
| RNF-07 | Seguridad | Las rutas protegidas deben exigir autenticación. | JWT Bearer. |
| RNF-08 | Seguridad | Las contraseñas no deben almacenarse en texto plano. | bcrypt con salt. |
| RNF-09 | Seguridad | Los secretos deben salir del código fuente. | Configuración mediante `.env`; requiere secretos fuertes en producción. |
| RNF-10 | Seguridad | Los archivos deben validarse por contenido y tamaño. | Magic bytes, extensión y límite configurable. |
| RNF-11 | Mantenibilidad | La lógica debe separarse por responsabilidades. | API, esquemas, servicios, repositorios, tareas, OCR, CV y RPA. |
| RNF-12 | Mantenibilidad | La configuración debe centralizarse. | Pydantic Settings. |
| RNF-13 | Portabilidad | La solución debe ejecutarse de forma reproducible. | Dockerfiles y Docker Compose. |
| RNF-14 | Escalabilidad | Debe ser posible aumentar workers sin cambiar la API. | Celery permite réplicas del worker. |
| RNF-15 | Observabilidad | Cada factura debe conservar una bitácora de etapas y resultados. | `processing_logs` y estados persistidos. |
| RNF-16 | Usabilidad | El frontend debe ser navegable desde escritorio y móvil. | Diseño responsivo y menú lateral adaptable. |
| RNF-17 | Usabilidad | Los estados deben presentarse con etiquetas legibles. | `StatusBadge` y mensajes de error. |
| RNF-18 | Compatibilidad | Deben aceptarse los formatos requeridos. | PDF, JPG, JPEG y PNG. |
| RNF-19 | Recuperación | Los datos persistentes deben sobrevivir al reinicio de contenedores. | Volúmenes Docker para PostgreSQL, Redis y RPA target. |
| RNF-20 | Trazabilidad | Reportes, correos y automatizaciones deben registrar usuario y fechas. | Tablas especializadas y llaves foráneas. |
| RNF-21 | Calidad | El frontend y backend deben compilar sin errores. | `npm run build` y `compileall` validados. |
| RNF-22 | Despliegue | La solución debe responder mediante HTTPS y URL pública. | URL pública operativa por HTTP; HTTPS pendiente. |

## 6. Funcionalidades opcionales implementadas

- Dashboard con métricas.
- Clasificación por proveedor y categoría.
- Procesamiento masivo.
- Detección de duplicados.
- Validación de NIT.
- Múltiples formatos de reporte.
- Gráficas administrativas.
- Procesamiento en segundo plano.
- Evidencia de ejecución RPA.

## 7. Funcionalidades de extensión

El esquema contiene estructuras preparadas para:

- detalle de líneas de factura;
- tareas programadas;
- configuración persistente;
- auditoría de APIs externas.

Estas estructuras no constituyen módulos funcionales completos en la versión actual.
