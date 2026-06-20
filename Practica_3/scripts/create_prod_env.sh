#!/usr/bin/env bash
set -euo pipefail
IP="${1:-}"
[[ -n "$IP" ]] || { echo "Uso: $0 IP_PUBLICA_EC2" >&2; exit 1; }
[[ ! -f .env.production ]] || { echo "Ya existe .env.production" >&2; exit 1; }
SECRET="$(openssl rand -hex 48)"
DBPASS="$(openssl rand -hex 24)"
RPAPASS="$(openssl rand -hex 18)"
cat > .env.production <<EOF
PROJECT_NAME=SmartInvoice
ENVIRONMENT=production
API_V1_PREFIX=/api/v1
SECRET_KEY=${SECRET}
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=480
POSTGRES_DB=smartinvoice
POSTGRES_USER=smartinvoice_user
POSTGRES_PASSWORD=${DBPASS}
POSTGRES_HOST=db
POSTGRES_PORT=5432
DATABASE_URL=postgresql://smartinvoice_user:${DBPASS}@db:5432/smartinvoice
REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/1
UPLOAD_DIR=/app/storage/uploads
PROCESSED_DIR=/app/storage/processed
REPORTS_DIR=/app/storage/reports
RPA_EVIDENCE_DIR=/app/storage/rpa
MAX_UPLOAD_SIZE_MB=15
TESSERACT_LANGUAGE=spa+eng
OCR_MIN_CONFIDENCE=60
OCR_DPI=300
MAX_PDF_PAGES=5
SMTP_HOST=mailhog
SMTP_PORT=1025
SMTP_USERNAME=
SMTP_PASSWORD=
SMTP_USE_TLS=false
SMTP_TIMEOUT_SECONDS=30
SMTP_FROM_EMAIL=notificaciones@smartinvoice.local
SMTP_FROM_NAME=SmartInvoice
RPA_TARGET_URL=http://rpa-target:8080
RPA_USERNAME=robot
RPA_PASSWORD=${RPAPASS}
VITE_API_URL=/api/v1
CORS_ORIGINS=http://${IP}
LOCAL_UID=$(id -u)
LOCAL_GID=$(id -g)
EOF
chmod 600 .env.production
echo "Creado .env.production para http://${IP}"
