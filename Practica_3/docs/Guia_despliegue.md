# Guía de despliegue

## 1. Estado

La ejecución local está completa y validada. La publicación en nube y las URL públicas deben completarse antes de la evaluación.

## 2. Topología recomendada

Para la práctica puede usarse una VM Linux:

```text
Internet
   |
HTTPS / proxy inverso
   |
VM Linux con Docker Compose
   |-- frontend
   |-- backend
   |-- worker
   |-- PostgreSQL
   |-- Redis
   |-- rpa-target
   `-- SMTP o MailHog restringido
```

## 3. Requisitos de la VM

Recomendación mínima:

- Ubuntu 22.04 o 24.04;
- 2 vCPU;
- 4 GB de RAM;
- 30 GB de almacenamiento;
- IP pública;
- puertos 80 y 443 abiertos;
- acceso SSH restringido.

OCR y Chromium pueden consumir memoria. Una instancia de 1 GB no es recomendable.

## 4. Preparación

```bash
sudo apt update
sudo apt install -y git ca-certificates curl
```

Instale Docker Engine y el complemento Compose según el proveedor.

Compruebe:

```bash
docker --version
docker compose version
```

## 5. Obtener el proyecto

```bash
git clone git@github.com:NelsonCun/-IA1-_VACASJUN2026_NelsonCun_201222010.git
cd ./-IA1-_VACASJUN2026_NelsonCun_201222010
git checkout practica_3
cd Practica_3
```

## 6. Variables de producción

```bash
cp .env.example .env
nano .env
```

Cambie obligatoriamente:

- `SECRET_KEY`;
- `POSTGRES_PASSWORD`;
- `RPA_PASSWORD`;
- `CORS_ORIGINS`;
- `VITE_API_URL`;
- credenciales SMTP;
- remitente SMTP.

Generar secreto:

```bash
openssl rand -hex 48
```

## 7. Ajustes necesarios

El Compose local expone puertos de desarrollo y usa `localhost` para el frontend. Antes del despliegue se debe crear una variante de producción que:

- use la URL pública de API;
- no exponga PostgreSQL ni Redis a Internet;
- sirva el frontend con Nginx;
- mantenga `backend`, `db`, `redis` y `worker` en red privada;
- publique únicamente 80/443;
- configure almacenamiento persistente;
- aplique reinicio automático;
- use HTTPS.

## 8. Arranque

```bash
docker compose up -d --build
docker compose ps
```

## 9. Validación

```bash
curl -fsS http://127.0.0.1:8001/api/v1/health
docker compose exec frontend npm run build
docker compose exec backend python -m compileall app
```

Pruebe:

- login;
- carga;
- OCR;
- reporte;
- RPA;
- correo.

## 10. Firewall

Ejemplo con UFW:

```bash
sudo ufw allow OpenSSH
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

No publique:

- 5432/5433;
- 6379;
- 1025;
- panel MailHog sin autenticación.

## 11. HTTPS

Use Nginx o Caddy. Las URLs finales deben anotarse aquí:

```text
Frontend: PENDIENTE_DE_DESPLIEGUE
API: PENDIENTE_DE_DESPLIEGUE
Swagger: PENDIENTE_DE_DESPLIEGUE
```

## 12. Persistencia y respaldo

Respaldo de PostgreSQL:

```bash
docker compose exec -T db \
  pg_dump \
  -U smartinvoice_user \
  -d smartinvoice \
  > backup_smartinvoice.sql
```

Respalde también:

```text
storage/uploads
storage/processed
storage/reports
storage/rpa
```

## 13. Actualización

```bash
git pull origin practica_3
docker compose up -d --build
docker compose ps
```

## 14. Diagnóstico

```bash
docker compose logs --tail=200 backend
docker compose logs --tail=200 worker
docker compose logs --tail=200 frontend
docker compose logs --tail=200 rpa-target
```

## 15. Criterio de aceptación

El despliegue está listo cuando:

- la URL pública abre el login;
- el health endpoint responde 200;
- la API accede a PostgreSQL y Redis;
- el worker procesa una factura;
- el reporte descarga;
- la RPA produce evidencia;
- el correo llega al SMTP configurado;
- los datos sobreviven a un reinicio.
