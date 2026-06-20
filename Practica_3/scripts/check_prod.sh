#!/usr/bin/env bash
set -euo pipefail
F=docker-compose.prod.yml
docker compose -f "$F" ps
curl -fsS http://127.0.0.1/api/v1/health | python3 -m json.tool
curl -fsSI http://127.0.0.1/ | sed -n '1,8p'
curl -fsSI http://127.0.0.1/docs | sed -n '1,8p'
docker compose -f "$F" exec -T worker celery -A app.tasks.celery_app.celery_app inspect ping
free -h
df -h /
