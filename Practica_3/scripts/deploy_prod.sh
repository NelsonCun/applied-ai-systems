#!/usr/bin/env bash
set -euo pipefail
F=docker-compose.prod.yml
[[ -f "$F" && -f .env.production ]] || { echo "Faltan archivos de producción" >&2; exit 1; }
mkdir -p storage/uploads storage/processed storage/reports storage/rpa
chmod 600 .env.production
docker compose -f "$F" config >/dev/null
docker compose -f "$F" pull db redis mailhog
docker compose -f "$F" build --pull
docker compose -f "$F" up -d
for i in $(seq 1 60); do
  curl -fsS http://127.0.0.1/api/v1/health >/tmp/smartinvoice-health.json && break
  sleep 5
done
curl -fsS http://127.0.0.1/api/v1/health >/tmp/smartinvoice-health.json
docker compose -f "$F" ps
python3 -m json.tool /tmp/smartinvoice-health.json
