#!/usr/bin/env bash
set -euo pipefail

# --- Start Debian's default Postgres cluster ---
PG_MAJOR="$(psql -V | awk '{print $3}' | cut -d. -f1)"
echo "🚀 Starting Postgres cluster ${PG_MAJOR}/main..."
pg_ctlcluster "${PG_MAJOR}" main start

# Wait till ready
for i in $(seq 1 60); do
  if pg_isready -h 127.0.0.1 -p 5432 -U postgres >/dev/null 2>&1; then
    echo "✅ Postgres is ready"
    break
  fi
  sleep 1
done

# --- app/DSN variables ---
: "${POSTGRES_USER:=app}"
: "${POSTGRES_PASSWORD:=local}"
: "${POSTGRES_DB:=appdb}"


# Creates role if it does not exist
if ! su -s /bin/bash postgres -c "psql -tAc \"SELECT 1 FROM pg_roles WHERE rolname='${POSTGRES_USER}'\"" | grep -q 1; then
  su -s /bin/bash postgres -c "psql -c \"CREATE USER ${POSTGRES_USER} WITH PASSWORD '${POSTGRES_PASSWORD}';\""
fi

# Creates DB if does not exist
if ! su -s /bin/bash postgres -c "psql -tAc \"SELECT 1 FROM pg_database WHERE datname='${POSTGRES_DB}'\"" | grep -q 1; then
  su -s /bin/bash postgres -c "psql -c \"CREATE DATABASE ${POSTGRES_DB} OWNER ${POSTGRES_USER};\""
fi

# Define DNS for app
export DATABASE_URL="${DATABASE_URL:-postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@127.0.0.1:5432/${POSTGRES_DB}}"
echo "🔗 DATABASE_URL=${DATABASE_URL}"

# Launch FastAPI
exec uvicorn main:app --host 0.0.0.0 --port 8000
