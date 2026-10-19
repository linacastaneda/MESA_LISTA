#!/usr/bin/env bash
set -euo pipefail
#El despliegue declara explícitamente la inicialización idempotente.
#No se cargan cuentas ni se borran filas durante el arranque.
flask --app run.py init-db
exec gunicorn 'reservas:create_app()' --bind "0.0.0.0:${PORT:-8000}" \
  --workers 1 --threads 4 --timeout 30 --access-logfile - --error-logfile -
