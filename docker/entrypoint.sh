#!/usr/bin/env bash
set -euo pipefail

# --- Start Debian's default Postgres cluster ---
PG_MAJOR="$(psql -V | awk '{print $3}' | cut -d. -f1)"
echo "🚀 Starting Postgres cluster ${PG_MAJOR}/main..."
pg_ctlcluster "${PG_MAJOR}" main start

# Espera a que esté listo (puedes seguir usando TCP para el check)
for i in $(seq 1 60); do
  if pg_isready -h 127.0.0.1 -p 5432 -U postgres >/dev/null 2>&1; then
    echo "✅ Postgres is ready"
    break
  fi
  sleep 1
done

# --- Variables de la app/DSN ---
: "${POSTGRES_USER:=app}"
: "${POSTGRES_PASSWORD:=local}"
: "${POSTGRES_DB:=appdb}"

# === IMPORTANTE: usar socket UNIX y el usuario del SO 'postgres' ===
# Crear rol si no existe
if ! su -s /bin/bash postgres -c "psql -tAc \"SELECT 1 FROM pg_roles WHERE rolname='${POSTGRES_USER}'\"" | grep -q 1; then
  su -s /bin/bash postgres -c "psql -c \"CREATE USER ${POSTGRES_USER} WITH PASSWORD '${POSTGRES_PASSWORD}';\""
fi

# Crear DB si no existe
if ! su -s /bin/bash postgres -c "psql -tAc \"SELECT 1 FROM pg_database WHERE datname='${POSTGRES_DB}'\"" | grep -q 1; then
  su -s /bin/bash postgres -c "psql -c \"CREATE DATABASE ${POSTGRES_DB} OWNER ${POSTGRES_USER};\""
fi

# DSN único para tu app (como quieres)
export DATABASE_URL="${DATABASE_URL:-postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@127.0.0.1:5432/${POSTGRES_DB}}"
echo "🔗 DATABASE_URL=${DATABASE_URL}"

# Arranca FastAPI
exec uvicorn main:app --host 0.0.0.0 --port 8000
