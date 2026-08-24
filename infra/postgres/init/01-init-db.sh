#!/usr/bin/env bash

set -euo pipefail

echo "Initializing GridPulse database..."

psql \
  -v ON_ERROR_STOP=1 \
  --username "$POSTGRES_USER" \
  --dbname "$POSTGRES_DB" \
  --set=app_user="$APP_DB_USER" \
  --set=app_password="$APP_DB_PASSWORD" <<'EOSQL'

CREATE EXTENSION IF NOT EXISTS timescaledb;

SELECT format(
    'CREATE ROLE %I LOGIN PASSWORD %L',
    :'app_user',
    :'app_password'
)
WHERE NOT EXISTS (
    SELECT 1
    FROM pg_roles
    WHERE rolname = :'app_user'
)
\gexec

GRANT USAGE ON SCHEMA public TO :"app_user";

ALTER DEFAULT PRIVILEGES
IN SCHEMA public
GRANT SELECT, INSERT, UPDATE, DELETE
ON TABLES
TO :"app_user";

ALTER DEFAULT PRIVILEGES
IN SCHEMA public
GRANT USAGE, SELECT
ON SEQUENCES
TO :"app_user";

EOSQL

echo "GridPulse database initialization complete."
