#!/usr/bin/env bash
set -euo pipefail

# Function: wait until Postgres responds
wait_for_pg() {
  echo "⏳ Waiting for Postgres on 127.0.0.1:${POSTGRES_PORT}..."
  for i in $(seq 1 60); do
    if pg_isready -h 127.0.0.1 -p "${POSTGRES_PORT}" -U postgres >/dev/null 2>&1; then
      echo "✅ Postgres is ready"
      return 0
    fi
    sleep 1
  done
  echo "❌ Postgres did not start in time"
  exit 1
}

# 1. Initialize cluster if not exists
if [ ! -s "$PGDATA/PG_VERSION" ]; then
  echo "📦 Initializing Postgres cluster in $PGDATA"
  mkdir -p "$PGDATA"
  chown -R postgres:postgres "$PGDATA"
  su -s /bin/bash postgres -c "initdb -D '$PGDATA' --locale=C.UTF-8"

  echo "listen_addresses = '127.0.0.1'" >> "$PGDATA/postgresql.conf"
  echo "port = ${POSTGRES_PORT}" >> "$PGDATA/postgresql.conf"
  echo "host all all 127.0.0.1/32 md5" >> "$PGDATA/pg_hba.conf"
fi

# 2. Start Postgres in background
echo "🚀 Starting Postgres..."
su -s /bin/bash postgres -c "pg_ctl -D '$PGDATA' -l /tmp/postgres.log start"

# 3. Wait for Postgres
wait_for_pg

# 4. Create role and DB if missing
echo "🔧 Ensuring user and database exist..."
psql -h 127.0.0.1 -p "${POSTGRES_PORT}" -U postgres -tc \
  "SELECT 1 FROM pg_roles WHERE rolname='${POSTGRES_USER}'" | grep -q 1 \
  || psql -h 127.0.0.1 -p "${POSTGRES_PORT}" -U postgres -c \
  "CREATE USER ${POSTGRES_USER} WITH PASSWORD '${POSTGRES_PASSWORD}';"

psql -h 127.0.0.1 -p "${POSTGRES_PORT}" -U postgres -tc \
  "SELECT 1 FROM pg_database WHERE datname='${POSTGRES_DB}'" | grep -q 1 \
  || psql -h 127.0.0.1 -p "${POSTGRES_PORT}" -U postgres -c \
  "CREATE DATABASE ${POSTGRES_DB} OWNER ${POSTGRES_USER};"

# 5. Launch FastAPI
echo "🌐 Starting FastAPI..."
exec uvicorn main:app --host 0.0.0.0 --port 8000
