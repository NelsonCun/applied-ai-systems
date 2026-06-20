# Configuración SMTP de SmartInvoice

## 1. Propósito

SmartInvoice incorpora un mecanismo de notificación por correo para distribuir los reportes generados por el sistema. El envío se ejecuta de forma asíncrona mediante Celery, de modo que la API no permanece bloqueada durante la conexión SMTP ni durante la transferencia del archivo adjunto.

El worker construye un mensaje MIME, adjunta el reporte solicitado, se autentica contra el servidor SMTP configurado y registra el resultado en la tabla `email_logs`.

## 2. Flujo funcional

```text
Usuario
  |
  | Solicita envío de reporte
  v
API FastAPI
  |
  | Encola tarea
  v
Redis / Celery
  |
  | Construye mensaje MIME
  | Adjunta reporte
  | Autentica mediante SMTP
  v
Servidor SMTP
  |
  v
Buzón del destinatario
```

El resultado de la operación queda persistido con los siguientes datos:

- destinatario;
- asunto;
- cuerpo del mensaje;
- reporte relacionado;
- estado del envío;
- identificador SMTP;
- mensaje de error, cuando corresponde;
- fecha de creación y fecha de envío.

## 3. Configuración por entorno

### 3.1 Desarrollo

El entorno local utiliza MailHog como servidor SMTP de prueba. Su propósito es inspeccionar destinatario, asunto, cuerpo y adjuntos sin entregar mensajes a Internet.

```env
SMTP_HOST=mailhog
SMTP_PORT=1025
SMTP_USERNAME=
SMTP_PASSWORD=
SMTP_USE_TLS=false
SMTP_TIMEOUT_SECONDS=30
SMTP_FROM_EMAIL=notificaciones@smartinvoice.local
SMTP_FROM_NAME=SmartInvoice
```

### 3.2 Producción

El despliegue público fue validado con Gmail SMTP, autenticación mediante contraseña de aplicación y cifrado STARTTLS sobre el puerto 587.

```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=CORREO_REMITENTE
SMTP_PASSWORD=CONTRASENA_DE_APLICACION
SMTP_USE_TLS=true
SMTP_TIMEOUT_SECONDS=30
SMTP_FROM_EMAIL=CORREO_REMITENTE
SMTP_FROM_NAME=SmartInvoice
```

La cuenta remitente requiere verificación en dos pasos. La credencial SMTP corresponde a una contraseña de aplicación y no a la contraseña principal de la cuenta.

## 4. Variables utilizadas

| Variable | Descripción |
|---|---|
| `SMTP_HOST` | Nombre o dirección del servidor SMTP. |
| `SMTP_PORT` | Puerto de conexión SMTP. |
| `SMTP_USERNAME` | Usuario empleado durante la autenticación. |
| `SMTP_PASSWORD` | Credencial del usuario SMTP. |
| `SMTP_USE_TLS` | Activa STARTTLS antes de autenticar. |
| `SMTP_TIMEOUT_SECONDS` | Tiempo máximo de espera de la conexión. |
| `SMTP_FROM_EMAIL` | Dirección mostrada como remitente. |
| `SMTP_FROM_NAME` | Nombre visible del remitente. |

## 5. Protección de secretos

Las credenciales reales se almacenan exclusivamente en `.env.production`. Este archivo se encuentra excluido del control de versiones y mantiene permisos restrictivos.

```bash
chmod 600 .env.production

git check-ignore -v .env.production

git ls-files .env.production
```

El archivo `.env.production.example` contiene únicamente marcadores de configuración. No almacena direcciones privadas, contraseñas de aplicación, secretos JWT ni credenciales de base de datos.

## 6. Aplicación de la configuración

Las variables de entorno se cargan durante el inicio de los contenedores. Cuando cambia la configuración SMTP, backend y worker se recrean sin necesidad de reconstruir las imágenes.

```bash
docker compose \
  --env-file .env.production \
  -f docker-compose.prod.yml \
  up -d \
  --no-deps \
  --force-recreate \
  backend worker
```

## 7. Verificación técnica

La configuración cargada en el worker puede validarse sin exponer la contraseña:

```bash
docker compose \
  --env-file .env.production \
  -f docker-compose.prod.yml \
  exec -T worker \
  python - <<'PY'
from app.core.config import settings

print("Host:", settings.smtp_host)
print("Puerto:", settings.smtp_port)
print("TLS:", settings.smtp_use_tls)
print("Usuario configurado:", bool(settings.smtp_username))
print("Contraseña configurada:", bool(settings.smtp_password))
print("Remitente:", settings.smtp_from_email)
PY
```

La autenticación SMTP se validó mediante una conexión STARTTLS y una operación `login` desde el worker:

```bash
docker compose \
  --env-file .env.production \
  -f docker-compose.prod.yml \
  exec -T worker \
  python - <<'PY'
import smtplib
import ssl

from app.core.config import settings

context = ssl.create_default_context()

with smtplib.SMTP(
    settings.smtp_host,
    settings.smtp_port,
    timeout=settings.smtp_timeout_seconds,
) as smtp:
    smtp.ehlo()

    if settings.smtp_use_tls:
        smtp.starttls(context=context)
        smtp.ehlo()

    smtp.login(
        settings.smtp_username,
        settings.smtp_password,
    )

print("Autenticación SMTP correcta.")
PY
```

## 8. Validación funcional realizada

La validación del flujo de correo incluyó:

1. generación de un reporte con estado `SUCCESS`;
2. selección de un destinatario real;
3. creación de la tarea Celery;
4. autenticación contra Gmail SMTP;
5. entrega del mensaje al buzón indicado;
6. recepción del archivo adjunto;
7. registro exitoso en `email_logs`.

El resultado confirmó que la aplicación realiza entrega externa real y no depende de MailHog en producción.

## 9. Diagnóstico

Los registros del worker permiten identificar errores de conexión, autenticación o entrega:

```bash
docker compose \
  --env-file .env.production \
  -f docker-compose.prod.yml \
  logs \
  --since=10m \
  worker
```

| Código o condición | Interpretación |
|---|---|
| `535` | Usuario o contraseña SMTP inválidos. |
| `534` | La cuenta requiere una contraseña de aplicación. |
| Timeout | No existe conectividad saliente hacia el puerto SMTP configurado. |
| Destinatario rechazado | Dirección inválida o política restrictiva del servidor. |
| Archivo inexistente | El reporte asociado no está disponible en el almacenamiento. |

## 10. Consideraciones operativas

- MailHog permanece disponible únicamente para desarrollo y pruebas aisladas.
- El servidor de producción utiliza una conexión SMTP saliente; no requiere publicar un puerto SMTP en EC2.
- La contraseña de aplicación puede revocarse al finalizar el período de evaluación o cuando deje de utilizarse el despliegue.
- La rotación de credenciales no requiere cambios en el código fuente.
- La trazabilidad del envío se conserva en PostgreSQL mediante `email_logs`.
