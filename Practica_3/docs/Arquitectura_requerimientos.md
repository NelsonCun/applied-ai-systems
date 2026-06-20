# Arquitectura y requerimientos — SmartInvoice

## 1. Información general

**Sistema:** SmartInvoice

**Curso:** Inteligencia Artificial 1

**Práctica:** Práctica 3, Vacaciones de junio 2026

**Estudiante:** Nelson Emanuel Cún Bálan

**Carné:** 201222010

**Universidad:** Universidad de San Carlos de Guatemala

**Facultad:** Facultad de Ingeniería

SmartInvoice es una plataforma web para automatizar el procesamiento administrativo de facturas digitales. La solución integra carga de documentos, Computer Vision, OCR, extracción estructurada, validación, persistencia, reportes, automatización RPA y entrega de reportes por correo.

---

## 2. Objetivo

Definir los requerimientos funcionales, no funcionales y reglas de negocio de SmartInvoice, así como la relación entre dichos requerimientos y la arquitectura implementada.

---

## 3. Alcance

La versión entregada comprende:

- autenticación administrativa;
- administración de proveedores;
- carga individual y masiva de facturas;
- soporte para PDF, JPG, JPEG y PNG;
- preprocesamiento mediante OpenCV;
- OCR local mediante Tesseract;
- extracción y validación de campos administrativos;
- revisión manual;
- detección de duplicados;
- dashboard;
- reportes PDF, XLSX y CSV;
- automatización RPA mediante Playwright;
- entrega de reportes mediante SMTP;
- bitácoras de procesamiento;
- despliegue mediante Docker Compose en AWS EC2.

La administración web de usuarios, HTTPS con dominio propio y almacenamiento de objetos externo se consideran extensiones futuras.

---

## 4. Actores del sistema

### 4.1 Administrador

Gestiona proveedores, carga y revisa facturas, consulta métricas, genera reportes, ejecuta automatizaciones y envía reportes por correo.

### 4.2 Operador

Accede a las funciones habilitadas por autenticación y participa en la carga, consulta y revisión de documentos.

### 4.3 Worker Celery

Ejecuta en segundo plano el pipeline OCR, la generación de reportes, la automatización RPA y el envío SMTP.

### 4.4 Sistema externo simulado

Recibe los datos ingresados por Playwright y devuelve un identificador del registro creado.

### 4.5 Servidor SMTP

Recibe el mensaje autenticado y entrega el reporte adjunto al destinatario indicado.

### 4.6 Servicios de infraestructura

PostgreSQL conserva la información estructurada; Redis actúa como broker y backend de resultados; Nginx publica el frontend y dirige las solicitudes hacia FastAPI.

---

## 5. Requerimientos funcionales

### RF-01 — Inicio de sesión

El sistema permite autenticarse mediante nombre de usuario o correo electrónico y contraseña.

**Datos de entrada:**

- Identificador de usuario.
- Contraseña.

**Validaciones:**

- Las credenciales deben corresponder a un usuario activo.
- La contraseña se valida mediante bcrypt.

**Resultado esperado:**

- Se emite un token JWT.
- El usuario accede al panel administrativo.

**Prioridad:** Alta.

---

### RF-02 — Validación de sesión

El sistema protege las rutas administrativas y verifica el token JWT antes de procesar una solicitud.

**Datos de entrada:**

- Token Bearer.

**Validaciones:**

- El token debe estar firmado, vigente y ser de tipo `access`.

**Resultado esperado:**

- La solicitud continúa con el usuario autenticado.
- Los tokens inválidos o vencidos producen respuesta no autorizada.

**Prioridad:** Alta.

---

### RF-03 — Cierre de sesión

La interfaz permite finalizar la sesión activa.

**Resultado esperado:**

- El token almacenado en el navegador se elimina.
- La aplicación retorna a la pantalla de acceso.

**Prioridad:** Media.

---

### RF-04 — Administración de proveedores

El administrador puede crear, consultar, actualizar, activar y desactivar proveedores.

**Datos de entrada:**

- Nombre.
- NIT.
- Correo, teléfono y dirección opcionales.
- Categoría.

**Validaciones:**

- El NIT debe cumplir el formato admitido.
- No se permiten NIT duplicados.
- El correo, cuando existe, debe tener formato válido.

**Resultado esperado:**

- El proveedor queda disponible para asociación con facturas.

**Prioridad:** Alta.

---

### RF-05 — Consulta de categorías

El sistema presenta las categorías activas utilizadas para clasificar proveedores y facturas.

**Resultado esperado:**

- Las categorías se muestran en formularios y filtros.

**Prioridad:** Media.

---

### RF-06 — Carga individual de factura

El usuario puede registrar una factura digital para procesamiento.

**Datos de entrada:**

- Archivo PDF, JPG, JPEG o PNG.
- Proveedor y categoría opcionales.

**Validaciones:**

- El archivo no puede estar vacío.
- La extensión debe coincidir con la firma binaria.
- El tamaño no puede superar el límite configurado.

**Resultado esperado:**

- La factura se registra con estado `PENDING`.
- Se crea la bitácora de carga.
- El trabajo se envía al worker Celery.

**Prioridad:** Alta.

---

### RF-07 — Carga masiva de facturas

El sistema admite la carga de hasta veinte documentos en una sola operación.

**Datos de entrada:**

- Conjunto de archivos compatibles.

**Validaciones:**

- La operación admite como máximo veinte archivos.
- Cada documento se valida de forma independiente.

**Resultado esperado:**

- Se devuelve el resultado individual de cada archivo.
- Los documentos válidos se encolan para procesamiento.

**Prioridad:** Alta.

---

### RF-08 — Validación de archivos

El sistema verifica extensión, contenido, tamaño y huella criptográfica de cada documento.

**Datos de entrada:**

- Archivo recibido.

**Validaciones:**

- Magic bytes compatibles.
- Tamaño máximo configurable.
- SHA-256 no registrado previamente como documento válido.

**Resultado esperado:**

- El archivo válido se conserva en almacenamiento.
- Los archivos incompatibles se rechazan con un mensaje controlado.

**Prioridad:** Alta.

---

### RF-09 — Preprocesamiento mediante Computer Vision

Cada documento se transforma para mejorar la legibilidad antes del OCR.

**Datos de entrada:**

- Documento original.

**Validaciones:**

- Los PDF se renderizan hasta el máximo de páginas configurado.

**Resultado esperado:**

- Se generan imágenes redimensionadas, corregidas, filtradas y binarizadas.
- Se registra la ruta del archivo procesado.

**Prioridad:** Alta.

---

### RF-10 — Reconocimiento óptico de caracteres

El sistema extrae texto mediante Tesseract OCR.

**Datos de entrada:**

- Imagen preprocesada.

**Validaciones:**

- Configuración de idioma y modo OCR definida por entorno.

**Resultado esperado:**

- Se almacena el texto reconocido.
- Se calcula la confianza promedio y la cantidad de palabras.

**Prioridad:** Alta.

---

### RF-11 — Extracción de campos administrativos

El parser identifica número, fecha, proveedor, NIT, subtotal, impuesto y total.

**Datos de entrada:**

- Texto OCR normalizado.

**Validaciones:**

- Montos no negativos.
- Fecha interpretable.
- Patrones compatibles para NIT y número de factura.

**Resultado esperado:**

- Los campos quedan disponibles en la factura y en `extracted_data`.

**Prioridad:** Alta.

---

### RF-12 — Asociación de proveedor

El sistema asocia la factura con un proveedor registrado.

**Datos de entrada:**

- NIT y nombre detectados.

**Validaciones:**

- Primero se busca coincidencia exacta por NIT.
- Cuando no existe coincidencia exacta se aplica similitud por nombre.

**Resultado esperado:**

- Se asigna `provider_id` cuando la coincidencia supera el umbral definido.

**Prioridad:** Alta.

---

### RF-13 — Validación administrativa

La factura se valida antes de considerarse procesada.

**Datos de entrada:**

- Campos extraídos.
- Confianza OCR.

**Validaciones:**

- Fecha no futura.
- NIT válido.
- Subtotal, impuesto y total consistentes.
- Confianza superior al mínimo configurado.

**Resultado esperado:**

- La factura cambia a `PROCESSED` o `REJECTED`.
- Los errores se almacenan en `validation_errors`.

**Prioridad:** Alta.

---

### RF-14 — Persistencia de resultados

El sistema almacena documento, metadatos, texto OCR, campos extraídos y estado.

**Datos de entrada:**

- Resultado del pipeline.

**Resultado esperado:**

- La información queda disponible en PostgreSQL y almacenamiento de archivos.

**Prioridad:** Alta.

---

### RF-15 — Consulta y filtrado de facturas

El usuario puede consultar facturas mediante paginación y filtros.

**Datos de entrada:**

- Texto de búsqueda.
- Estado.
- Proveedor.
- Rango o parámetros disponibles.

**Resultado esperado:**

- Se presenta una lista ordenada con información administrativa y estado.

**Prioridad:** Alta.

---

### RF-16 — Visualización de documentos

El detalle de factura permite consultar el archivo original y la imagen preprocesada.

**Datos de entrada:**

- Identificador de factura.

**Validaciones:**

- El usuario debe estar autenticado.
- El archivo debe existir.

**Resultado esperado:**

- El navegador recibe el documento correspondiente.

**Prioridad:** Media.

---

### RF-17 — Consulta de OCR y bitácora

El detalle presenta el texto OCR y las etapas ejecutadas.

**Datos de entrada:**

- Identificador de factura.

**Resultado esperado:**

- Se muestran confianza, texto reconocido, resultados y eventos del procesamiento.

**Prioridad:** Alta.

---

### RF-18 — Revisión manual

Las facturas rechazadas pueden corregirse y confirmarse manualmente.

**Datos de entrada:**

- Número.
- Fecha.
- Proveedor.
- Categoría.
- NIT.
- Subtotal.
- Impuesto.
- Total.

**Validaciones:**

- Los datos deben cumplir las mismas reglas de validación.
- Una factura duplicada no puede confirmarse.

**Resultado esperado:**

- La factura queda confirmada y cambia a `PROCESSED` cuando los datos son válidos.

**Prioridad:** Alta.

---

### RF-19 — Detección de duplicados

El sistema evita registrar dos veces el mismo documento o la misma factura lógica.

**Datos de entrada:**

- SHA-256.
- Proveedor.
- Número de factura.

**Validaciones:**

- Índice único parcial por huella.
- Combinación lógica proveedor y número.

**Resultado esperado:**

- El documento se marca como `DUPLICATE` y referencia la factura original cuando corresponde.

**Prioridad:** Alta.

---

### RF-20 — Dashboard administrativo

El sistema presenta métricas operativas y financieras.

**Resultado esperado:**

- Se muestran cantidades por estado, total procesado, IVA, confianza y agrupaciones por proveedor o período.

**Prioridad:** Media.

---

### RF-21 — Generación de reportes

El usuario puede generar reportes administrativos en PDF, XLSX y CSV.

**Datos de entrada:**

- Formato.
- Proveedor opcional.
- Estado opcional.
- Fechas opcionales.

**Validaciones:**

- Los filtros se aplican sobre los datos de factura.
- La generación se ejecuta en segundo plano.

**Resultado esperado:**

- Se registra un reporte con estado y archivo descargable.

**Prioridad:** Alta.

---

### RF-22 — Descarga de reportes

Los reportes finalizados pueden descargarse desde la interfaz.

**Datos de entrada:**

- Identificador del reporte.

**Validaciones:**

- El reporte debe tener estado `SUCCESS` y archivo existente.

**Resultado esperado:**

- El navegador recibe el archivo con su nombre y tipo correctos.

**Prioridad:** Alta.

---

### RF-23 — Automatización RPA

El sistema registra una factura procesada en un sistema web externo simulado.

**Datos de entrada:**

- Factura en estado `PROCESSED`.

**Validaciones:**

- El servicio externo debe estar disponible.
- La factura debe contener los datos requeridos.

**Resultado esperado:**

- Playwright completa el formulario, obtiene el identificador externo y registra el resultado.

**Prioridad:** Alta.

---

### RF-24 — Evidencia RPA

Cada ejecución RPA conserva estado, resultado y captura gráfica.

**Datos de entrada:**

- Ejecución de automatización.

**Resultado esperado:**

- La evidencia queda disponible para consulta y descarga.

**Prioridad:** Alta.

---

### RF-25 — Envío de reportes por correo

El sistema entrega un reporte a un destinatario mediante SMTP autenticado.

**Datos de entrada:**

- Reporte finalizado.
- Correo destinatario.
- Asunto y cuerpo.

**Validaciones:**

- El reporte debe tener estado `SUCCESS`.
- La dirección debe tener formato válido.
- El servidor SMTP debe aceptar autenticación.

**Resultado esperado:**

- El correo se entrega con archivo adjunto.
- El resultado se registra en `email_logs`.

**Prioridad:** Alta.

---

### RF-26 — Historial de correos

El usuario puede consultar los envíos realizados.

**Datos de entrada:**

- Filtros y paginación disponibles.

**Resultado esperado:**

- Se muestran destinatario, asunto, reporte, estado, fechas e información de error.

**Prioridad:** Media.

---

### RF-27 — Bitácora por etapa

El pipeline registra el inicio, resultado, duración y detalles de cada etapa.

**Datos de entrada:**

- Evento de procesamiento.

**Resultado esperado:**

- La trazabilidad queda almacenada en `processing_logs`.

**Prioridad:** Alta.

---

### RF-28 — Procesamiento asíncrono

Las operaciones intensivas se ejecutan fuera del ciclo HTTP principal.

**Datos de entrada:**

- Tarea encolada.

**Resultado esperado:**

- Celery procesa OCR, reportes, RPA y correo mediante Redis.

**Prioridad:** Alta.

---

### RF-29 — Procesamiento de lote de evaluación

El sistema procesa al menos veinte facturas de prueba.

**Datos de entrada:**

- Lote `samples/batch_20`.

**Validaciones:**

- Los documentos deben atravesar el pipeline completo.

**Resultado esperado:**

- Resultado validado de veinte facturas procesadas correctamente.

**Prioridad:** Alta.

---

### RF-30 — Ejecución mediante contenedores

La solución se ejecuta de forma reproducible mediante Docker Compose.

**Datos de entrada:**

- Archivos de configuración y variables de entorno.

**Resultado esperado:**

- Los servicios se crean en una red privada y conservan datos mediante volúmenes.

**Prioridad:** Alta.

---

### RF-31 — Acceso público

La aplicación se encuentra disponible mediante una dirección pública durante la evaluación.

**Datos de entrada:**

- Instancia AWS EC2 y grupo de seguridad.

**Validaciones:**

- El frontend debe responder en el puerto público configurado.
- Los servicios internos no se exponen directamente.

**Resultado esperado:**

- Frontend, API y Swagger accesibles mediante la IPv4 pública.

**Prioridad:** Alta.

---

## 6. Reglas de negocio

1. El tamaño máximo de archivo es configurable y tiene un valor de desarrollo de 15 MB.
2. Una carga masiva admite como máximo veinte documentos.
3. La extensión declarada debe coincidir con la firma binaria del archivo.
4. El SHA-256 identifica duplicados físicos.
5. La combinación proveedor y número de factura identifica duplicados lógicos.
6. Una factura duplicada no puede reprocesarse ni confirmarse.
7. La fecha de factura no puede ubicarse en el futuro.
8. Subtotal, impuesto y total no pueden ser negativos.
9. La diferencia entre subtotal más impuesto y total no puede superar Q0.10.
10. El NIT admite `CF`, nueve dígitos o el formato histórico con guion y dígito verificador.
11. La confianza mínima de OCR se define mediante `OCR_MIN_CONFIDENCE`.
12. Los PDF se procesan hasta el límite indicado por `MAX_PDF_PAGES`.
13. Solo las facturas `PROCESSED` participan en RPA.
14. Solo los reportes `SUCCESS` pueden descargarse o enviarse por correo.
15. Las credenciales y secretos se obtienen desde variables de entorno y no se almacenan en Git.

---

## 7. Requerimientos no funcionales

| ID | Categoría | Requerimiento | Evidencia de implementación |
|---|---|---|---|
| RNF-01 | Rendimiento | Las operaciones intensivas no deben bloquear la API. | Celery y Redis desacoplan OCR, reportes, RPA y correo. |
| RNF-02 | Capacidad | El sistema debe admitir lotes de veinte facturas. | Lote `L20A` validado 20/20. |
| RNF-03 | Disponibilidad | Los servicios críticos deben exponer comprobaciones de salud. | Healthchecks de PostgreSQL, Redis, backend, frontend y RPA Target. |
| RNF-04 | Integridad | Los montos, NIT y fechas deben validarse antes de confirmar. | Validaciones de servicio y restricciones SQL. |
| RNF-05 | Integridad | El mismo documento no debe registrarse dos veces. | SHA-256 e índice único parcial. |
| RNF-06 | Seguridad | Las rutas administrativas deben exigir autenticación. | JWT Bearer y rutas protegidas. |
| RNF-07 | Seguridad | Las contraseñas no deben almacenarse en texto plano. | bcrypt con salt. |
| RNF-08 | Seguridad | Los secretos deben permanecer fuera del repositorio. | `.env` y `.env.production` ignorados por Git. |
| RNF-09 | Seguridad | Los documentos deben validarse por contenido y tamaño. | Magic bytes, extensión y límite configurable. |
| RNF-10 | Mantenibilidad | La lógica debe separarse por responsabilidades. | Rutas, esquemas, servicios, repositorios, tareas, OCR, CV y RPA. |
| RNF-11 | Mantenibilidad | La configuración debe centralizarse. | Pydantic Settings. |
| RNF-12 | Portabilidad | La solución debe ejecutarse de forma reproducible. | Dockerfiles y Docker Compose. |
| RNF-13 | Escalabilidad | Debe ser posible aumentar workers sin modificar la API. | Celery admite réplicas del worker. |
| RNF-14 | Observabilidad | Cada factura debe conservar trazabilidad por etapa. | `processing_logs`, estados y duración. |
| RNF-15 | Usabilidad | El frontend debe adaptarse a escritorio y dispositivos pequeños. | Diseño responsivo y navegación lateral adaptable. |
| RNF-16 | Compatibilidad | Deben aceptarse los formatos requeridos. | PDF, JPG, JPEG y PNG. |
| RNF-17 | Recuperación | Los datos deben sobrevivir a reinicios de contenedores. | Volúmenes Docker y almacenamiento persistente. |
| RNF-18 | Trazabilidad | Reportes, correos y automatizaciones deben registrar usuario y fechas. | Tablas especializadas y llaves foráneas. |
| RNF-19 | Calidad | Backend y frontend deben compilar correctamente. | `compileall` y `npm run build` validados. |
| RNF-20 | Despliegue | La solución debe estar disponible en nube durante la evaluación. | AWS EC2 con IPv4 pública y Nginx. |

---

## 8. Relación entre requerimientos y arquitectura

| Grupo funcional | Componentes responsables |
|---|---|
| Autenticación | React, FastAPI, JWT, bcrypt, tabla `users`. |
| Proveedores | Rutas, servicios, repositorios, tablas `providers` e `invoice_categories`. |
| Facturas | API, almacenamiento, PostgreSQL y worker Celery. |
| Computer Vision y OCR | PyMuPDF, OpenCV, Tesseract y Pytesseract. |
| Validación | Parser, validadores, servicio de procesamiento y revisión manual. |
| Reportes | Celery, ReportLab, OpenPyXL, CSV y tabla `reports`. |
| RPA | Playwright, Chromium, RPA Target y tabla `automation_runs`. |
| Correo | Celery, SMTP autenticado y tabla `email_logs`. |
| Despliegue | Docker Compose, Nginx, AWS EC2 y volúmenes. |

---

## 9. Estado de cumplimiento

La versión entregada cumple los requerimientos principales del enunciado. El lote de evaluación alcanzó veinte facturas procesadas correctamente, el despliegue público respondió mediante AWS EC2 y el envío SMTP fue validado con entrega a un destinatario real.
