FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PGDATA=/var/lib/postgresql/data \
    PATH="/usr/lib/postgresql/16/bin:${PATH}"

# System dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev \
    postgresql-16 postgresql-client-16 postgresql-contrib-16 \
    curl ca-certificates \
 && rm -rf /var/lib/apt/lists/*

# App workspace
WORKDIR /app
COPY requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt
COPY . /app

# Entrypoint
COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Expose FastAPI (8000) and Postgres (5432)
EXPOSE 8000 5432

# Default DB env vars (override at runtime if needed)
ENV POSTGRES_USER=app \
    POSTGRES_PASSWORD=app \
    POSTGRES_DB=appdb \
    POSTGRES_PORT=5432 \
    DATABASE_URL=postgresql://app:app@127.0.0.1:5432/appdb

CMD ["/entrypoint.sh"]
