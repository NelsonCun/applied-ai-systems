# Guía de despliegue de SmartInvoice

## 1. Objetivo

Este documento describe la infraestructura, configuración y secuencia empleadas para desplegar SmartInvoice en AWS EC2 mediante Docker Compose.

## 2. Estado del despliegue

> **Historical deployment note:** this guide documents an AWS EC2 deployment that was successfully validated during the project lifecycle. The original public IP is intentionally omitted because the instance is not presented as a currently maintained portfolio endpoint.

La solución fue desplegada y validada en una instancia AWS EC2 con Ubuntu Server 24.04 LTS.

```text
```

La dirección corresponde a la IPv4 pública utilizada durante la validación final. Una asignación diferente de IP requiere actualizar `CORS_ORIGINS` y las referencias documentales del entorno.

## 3. Infraestructura utilizada

| Recurso | Configuración validada |
|---|---|
| Proveedor | AWS EC2 |
| Sistema operativo | Ubuntu Server 24.04 LTS x86_64 |
| Procesador | 2 vCPU |
| Memoria | 4 GiB |
| Swap | 2 GiB |
| Almacenamiento | 30 GiB EBS gp3 |
| Exposición pública | Puertos 22 y 80 |
| Orquestación | Docker Compose |
| Acceso al repositorio | Deploy Key SSH de solo lectura |

La capacidad seleccionada soportó PostgreSQL, Redis, FastAPI, Celery, Tesseract, OpenCV, Chromium, Nginx y el servicio RPA dentro de una misma máquina virtual.

## 4. Topología

```text
Internet
   |
Puerto 80
   |
Nginx
   |-- /          -> frontend React
   |-- /api/      -> FastAPI
   |-- /docs      -> Swagger
   |
Red Docker privada
   |-- PostgreSQL
   |-- Redis
   |-- Celery Worker
   |-- RPA Target
   |-- MailHog (solo desarrollo)
   `-- SMTP externo
```

PostgreSQL, Redis, backend, RPA Target y MailHog no se publican directamente en Internet.

## 5. Servicios productivos

| Servicio | Función | Exposición |
|---|---|---|
| `frontend` | Nginx y aplicación React compilada | Puerto 80 público |
| `backend` | API REST FastAPI | Red Docker |
| `worker` | OCR, reportes, RPA y correo | Red Docker |
| `db` | PostgreSQL 16 | Red Docker |
| `redis` | Broker y backend de resultados | Red Docker |
| `rpa-target` | Sistema externo simulado | Red Docker |
| `mailhog` | Captura SMTP de desarrollo | `127.0.0.1:8025` |

## 6. Obtención del código

El repositorio privado se clonó mediante una Deploy Key SSH de solo lectura.

```bash
git clone \
  --branch practica_3 \
  --single-branch \
  git@github.com:NelsonCun/-IA1-_VACASJUN2026_NelsonCun_201222010.git

cd \
  ./-IA1-_VACASJUN2026_NelsonCun_201222010/Practica_3
```

## 7. Preparación de la instancia

El script `scripts/bootstrap_ec2.sh` instala Docker Engine, Docker Compose y las dependencias básicas, además de crear un archivo swap de 2 GiB.

```bash
./scripts/bootstrap_ec2.sh
```

Redis utiliza la siguiente configuración del kernel:

```bash
echo 'vm.overcommit_memory=1' \
  | sudo tee \
    /etc/sysctl.d/98-smartinvoice-redis.conf

sudo sysctl --system
```

## 8. Configuración de producción

El archivo `.env.production` se genera a partir de la IP pública y permanece fuera del control de versiones.

```bash
./scripts/create_prod_env.sh EC2_PUBLIC_IP

chmod 600 .env.production
```

Las variables principales incluyen:

- `DATABASE_URL`;
- `REDIS_URL`;
- `CELERY_BROKER_URL`;
- `CELERY_RESULT_BACKEND`;
- `SECRET_KEY`;
- `CORS_ORIGINS`;
- `RPA_TARGET_URL`;
- variables SMTP;
- directorios de almacenamiento.

## 9. Configuración SMTP productiva

El entorno público utiliza Gmail SMTP con autenticación y STARTTLS:

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

La credencial corresponde a una contraseña de aplicación asociada a una cuenta con verificación en dos pasos. El archivo `.env.production.example` conserva únicamente marcadores y no contiene secretos reales.

La configuración detallada se encuentra en [Configuración SMTP](Configuracion_SMTP.md).

## 10. Construcción y arranque

El despliegue se ejecuta mediante:

```bash
./scripts/deploy_prod.sh
```

Este proceso realiza las siguientes operaciones:

1. validación de `docker-compose.prod.yml`;
2. descarga de imágenes base;
3. construcción de backend, frontend y RPA Target;
4. creación de red y volúmenes;
5. inicio de los siete servicios;
6. espera del endpoint de salud;
7. presentación del estado final.

## 11. Verificación del despliegue

El estado de los servicios se valida con:

```bash
docker compose \
  --env-file .env.production \
  -f docker-compose.prod.yml \
  ps

./scripts/check_prod.sh
```

El endpoint principal de salud es:

```bash
curl -fsS \
  http://127.0.0.1/api/v1/health \
  | python3 -m json.tool
```

La respuesta validada fue:

```json
{
  "status": "healthy",
  "application": "SmartInvoice",
  "environment": "production",
  "services": {
    "database": "available",
    "redis": "available"
  }
}
```

Celery también fue validado mediante `inspect ping`, con respuesta `pong` del worker.

## 12. Validación funcional en nube

El despliegue público fue verificado con los siguientes casos:

- acceso al frontend desde Internet;
- autenticación administrativa;
- carga de facturas;
- ejecución de Computer Vision y OCR;
- consulta de bitácora;
- generación y descarga de reportes;
- automatización RPA con evidencia;
- envío de reportes a un correo real;
- persistencia de datos en volúmenes Docker.

## 13. Seguridad de red

El Security Group permite únicamente:

| Puerto | Uso |
|---:|---|
| 22 | Administración SSH restringida |
| 80 | Aplicación web pública |

Los siguientes puertos permanecen sin exposición pública:

- PostgreSQL: `5432`;
- Redis: `6379`;
- backend: `8000`;
- RPA Target: `8080`;
- SMTP de desarrollo: `1025`;
- interfaz MailHog: `8025`.

El envío SMTP utiliza una conexión saliente desde el worker hacia el puerto 587 del proveedor externo.

## 14. Persistencia

La solución utiliza volúmenes Docker para:

- PostgreSQL;
- Redis;
- base de datos del RPA Target.

Los documentos y resultados se almacenan en:

```text
storage/uploads
storage/processed
storage/reports
storage/rpa
```

Un respaldo lógico de PostgreSQL puede generarse con:

```bash
docker compose \
  --env-file .env.production \
  -f docker-compose.prod.yml \
  exec -T db \
  sh -lc '
    pg_dump \
      -U "$POSTGRES_USER" \
      -d "$POSTGRES_DB"
  ' \
  > backup_smartinvoice.sql
```

## 15. Actualización del despliegue

La actualización del código utiliza la rama `practica_3`:

```bash
git pull --ff-only origin practica_3

docker compose \
  --env-file .env.production \
  -f docker-compose.prod.yml \
  up -d --build
```

Los cambios exclusivamente documentales no requieren reconstrucción de contenedores.

## 16. Diagnóstico

Los registros principales se consultan mediante:

```bash
docker compose \
  --env-file .env.production \
  -f docker-compose.prod.yml \
  logs \
  --tail=200 \
  backend worker frontend rpa-target
```

Los recursos de la instancia se verifican con:

```bash
free -h

df -h /

docker stats --no-stream
```
