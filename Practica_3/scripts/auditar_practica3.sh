#!/usr/bin/env bash
set -u

OUT="${1:-/tmp/auditoria_practica3.txt}"

exec > >(tee "$OUT") 2>&1

section() {
  printf '\n\n============================================================\n'
  printf '%s\n' "$1"
  printf '============================================================\n'
}

run() {
  printf '\n$ %s\n' "$*"
  "$@" || true
}

section "AUDITORÍA SMARTINVOICE - PRÁCTICA 3 IA1"
date
printf 'Directorio: %s\n' "$(pwd)"

if [[ ! -f docker-compose.yml && ! -f compose.yml && ! -f compose.yaml ]]; then
  echo "ADVERTENCIA: ejecute este script desde la raíz de Practica_3."
fi

section "1. ESTADO DE GIT"
run git status --short
run git branch --show-current
run git log -12 --oneline --decorate

section "2. ESTRUCTURA PRINCIPAL"
run find . -maxdepth 2 -type f \
  ! -path './.git/*' \
  ! -path './frontend/node_modules/*' \
  ! -path './frontend/dist/*' \
  | sort

section "3. DOCUMENTACIÓN Y ENTREGABLES"
run find . -type f \
  \( -iname '*.md' -o -iname '*.drawio' -o -iname '*.puml' \
     -o -iname '*.mmd' -o -iname '*.png' -o -iname '*.pdf' \) \
  ! -path './.git/*' \
  ! -path './frontend/node_modules/*' \
  ! -path './frontend/dist/*' \
  ! -path './storage/*' \
  | sort

echo
echo "Encabezados encontrados en documentación Markdown:"
grep -RInE \
  '^(#|##|###) +(Arquitectura|Requerimientos funcionales|Requerimientos no funcionales|Instalación|Ejecución|Despliegue|OCR|Computer Vision|RPA|API REST|Base de datos|Mejoras futuras|Bitácora|Pruebas)' \
  --include='*.md' . \
  --exclude-dir=.git \
  --exclude-dir=node_modules \
  --exclude-dir=dist || true

section "4. DOCKER Y DESPLIEGUE"
run docker compose config --services
run docker compose ps
run find . -maxdepth 4 -type f \
  \( -iname 'Dockerfile*' -o -iname '*compose*.yml' \
     -o -iname '*compose*.yaml' -o -iname '.env.example' \
     -o -iname 'render.yaml' -o -iname 'railway.json' \
     -o -iname 'Procfile' -o -iname '*.tf' \
     -o -iname 'appspec.yml' -o -iname 'task-definition*.json' \
     -o -iname 'cloudbuild.yaml' \) \
  ! -path './.git/*' \
  ! -path './frontend/node_modules/*' \
  | sort

section "5. PRUEBAS AUTOMATIZADAS"
run find . -type f \
  \( -iname 'test_*.py' -o -iname '*_test.py' \
     -o -iname '*.spec.js' -o -iname '*.test.js' \
     -o -iname '*.spec.jsx' -o -iname '*.test.jsx' \) \
  ! -path './.git/*' \
  ! -path './frontend/node_modules/*' \
  | sort

echo
echo "Configuraciones de pruebas:"
run find . -maxdepth 4 -type f \
  \( -iname 'pytest.ini' -o -iname 'pyproject.toml' \
     -o -iname 'tox.ini' -o -iname 'vitest.config.*' \
     -o -iname 'jest.config.*' \) \
  ! -path './.git/*' \
  | sort

section "6. COMPILACIÓN Y SALUD"
run docker compose exec -T backend python -m compileall app
run docker compose exec -T frontend npm run build
run curl -fsS -o /dev/null -w 'Backend health: HTTP %{http_code}\n' \
  http://localhost:8001/api/v1/health
run curl -fsS -o /dev/null -w 'Frontend: HTTP %{http_code}\n' \
  http://localhost:5174/
run curl -fsS -o /dev/null -w 'MailHog: HTTP %{http_code}\n' \
  http://localhost:8025/
run curl -fsS -o /dev/null -w 'RPA target: HTTP %{http_code}\n' \
  http://localhost:8082/

section "7. RUTAS DE LA API"
if curl -fsS http://localhost:8001/openapi.json \
  -o /tmp/smartinvoice-openapi-audit.json; then
  python3 - <<'PY'
import json
from pathlib import Path

doc = json.loads(
    Path("/tmp/smartinvoice-openapi-audit.json").read_text()
)

methods = {"get", "post", "put", "patch", "delete"}

for path, operations in sorted(doc.get("paths", {}).items()):
    for method in operations:
        if method.lower() in methods:
            print(f"{method.upper():7} {path}")
PY
else
  echo "No fue posible obtener OpenAPI."
fi

section "8. BASE DE DATOS - CONTEOS Y COBERTURA"
docker compose exec -T db \
  psql \
  -U smartinvoice_user \
  -d smartinvoice \
  -P pager=off \
  -c "
    SELECT 'users' AS entidad, COUNT(*) AS total FROM users
    UNION ALL
    SELECT 'providers', COUNT(*) FROM providers
    UNION ALL
    SELECT 'categories', COUNT(*) FROM categories
    UNION ALL
    SELECT 'invoices', COUNT(*) FROM invoices
    UNION ALL
    SELECT 'processing_logs', COUNT(*) FROM processing_logs
    UNION ALL
    SELECT 'reports', COUNT(*) FROM reports
    UNION ALL
    SELECT 'automation_runs', COUNT(*) FROM automation_runs
    UNION ALL
    SELECT 'email_logs', COUNT(*) FROM email_logs
    ORDER BY entidad;
  " || true

echo
echo "Estados de facturas:"
docker compose exec -T db \
  psql \
  -U smartinvoice_user \
  -d smartinvoice \
  -P pager=off \
  -c "
    SELECT status, COUNT(*) AS total
    FROM invoices
    GROUP BY status
    ORDER BY status;
  " || true

echo
echo "Formatos cargados:"
docker compose exec -T db \
  psql \
  -U smartinvoice_user \
  -d smartinvoice \
  -P pager=off \
  -c "
    SELECT
      LOWER(
        COALESCE(
          NULLIF(
            SUBSTRING(original_file_name FROM '\\.([^.]+)$'),
            ''
          ),
          'sin_extension'
        )
      ) AS extension,
      COUNT(*) AS total
    FROM invoices
    GROUP BY extension
    ORDER BY extension;
  " || true

echo
echo "Cobertura de campos OCR:"
docker compose exec -T db \
  psql \
  -U smartinvoice_user \
  -d smartinvoice \
  -P pager=off \
  -c "
    SELECT
      COUNT(*) AS total_facturas,
      COUNT(invoice_number) AS con_numero,
      COUNT(invoice_date) AS con_fecha,
      COUNT(provider_id) AS con_proveedor,
      COUNT(detected_nit) AS con_nit,
      COUNT(subtotal) AS con_subtotal,
      COUNT(tax) AS con_impuestos,
      COUNT(total) AS con_total,
      COUNT(ocr_text) AS con_texto_ocr,
      COUNT(processed_file_path) AS con_imagen_procesada
    FROM invoices;
  " || true

echo
echo "Bitácora por etapa y estado:"
docker compose exec -T db \
  psql \
  -U smartinvoice_user \
  -d smartinvoice \
  -P pager=off \
  -c "
    SELECT stage, status, COUNT(*) AS total
    FROM processing_logs
    GROUP BY stage, status
    ORDER BY stage, status;
  " || true

echo
echo "Últimas facturas:"
docker compose exec -T db \
  psql \
  -U smartinvoice_user \
  -d smartinvoice \
  -P pager=off \
  -c "
    SELECT
      id,
      original_file_name,
      invoice_number,
      status,
      provider_id,
      duplicate_of_invoice_id,
      ocr_confidence,
      created_at,
      processed_at
    FROM invoices
    ORDER BY id DESC
    LIMIT 25;
  " || true

section "9. ARCHIVOS DE PRUEBA DISPONIBLES"
find . -type f \
  \( -iname '*.pdf' -o -iname '*.jpg' -o -iname '*.jpeg' -o -iname '*.png' \) \
  ! -path './.git/*' \
  ! -path './frontend/node_modules/*' \
  ! -path './frontend/dist/*' \
  ! -path './storage/*' \
  -printf '%p\n' \
  | sort

echo
echo "Cantidad de archivos de prueba fuera de storage:"
find . -type f \
  \( -iname '*.pdf' -o -iname '*.jpg' -o -iname '*.jpeg' -o -iname '*.png' \) \
  ! -path './.git/*' \
  ! -path './frontend/node_modules/*' \
  ! -path './frontend/dist/*' \
  ! -path './storage/*' \
  | wc -l

section "10. CONFIGURACIÓN Y SECRETOS"
echo "Archivos .env versionados o presentes:"
find . -maxdepth 4 -type f \
  \( -name '.env' -o -name '.env.*' \) \
  ! -path './.git/*' \
  ! -path './frontend/node_modules/*' \
  -printf '%p\n' \
  | sort

echo
echo "Archivos ignorados relevantes:"
run git check-ignore -v \
  .env \
  backend/.env \
  frontend/.env \
  storage \
  frontend/node_modules \
  frontend/dist

section "11. README PRINCIPAL"
for candidate in README.md readme.md docs/README.md; do
  if [[ -f "$candidate" ]]; then
    echo
    echo "----- $candidate -----"
    sed -n '1,260p' "$candidate"
  fi
done

section "12. RESUMEN AUTOMÁTICO"
invoice_count="$(
  docker compose exec -T db \
    psql -U smartinvoice_user -d smartinvoice -tAc \
    "SELECT COUNT(*) FROM invoices;" 2>/dev/null \
  | tr -d '[:space:]'
)"

processed_count="$(
  docker compose exec -T db \
    psql -U smartinvoice_user -d smartinvoice -tAc \
    "SELECT COUNT(*) FROM invoices WHERE status IN ('PROCESSED','DUPLICATE','REJECTED');" \
    2>/dev/null | tr -d '[:space:]'
)"

printf 'Facturas registradas: %s\n' "${invoice_count:-desconocido}"
printf 'Facturas con resultado final: %s\n' "${processed_count:-desconocido}"

if [[ "${invoice_count:-0}" =~ ^[0-9]+$ ]] && (( invoice_count >= 20 )); then
  echo "REQUISITO 20 FACTURAS: CUMPLIDO EN CANTIDAD"
else
  echo "REQUISITO 20 FACTURAS: PENDIENTE"
fi

if find . -maxdepth 4 -type f \
  \( -iname 'render.yaml' -o -iname 'railway.json' \
     -o -iname '*.tf' -o -iname 'cloudbuild.yaml' \
     -o -iname 'appspec.yml' \) \
  | grep -q .; then
  echo "ARTEFACTOS DE NUBE: ENCONTRADOS"
else
  echo "ARTEFACTOS DE NUBE: NO ENCONTRADOS EN RUTAS COMUNES"
fi

echo
echo "Auditoría guardada en: $OUT"
