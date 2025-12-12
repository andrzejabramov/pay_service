#!/bin/bash
set -e

echo "Создаём пользователя репликации..."
psql -v ON_ERROR_STOP=1 --username "${POSTGRES_USER}" --dbname "postgres" <<-EOSQL
    CREATE USER ${REPLICATION_USER} WITH REPLICATION ENCRYPTED PASSWORD '${REPLICATION_PASSWORD}';
EOSQL

echo "Создаём прикладного пользователя ${APP_READER_USER}..."
psql -v ON_ERROR_STOP=1 --username "${POSTGRES_USER}" --dbname "${POSTGRES_DB}" <<-EOSQL
    DO \$\$
    BEGIN
        IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = '${APP_READER_USER}') THEN
            CREATE USER ${APP_READER_USER} WITH PASSWORD '${APP_READER_PASSWORD}';
        END IF;
    END
    \$\$;
EOSQL

echo "Пользователи созданы ✅"