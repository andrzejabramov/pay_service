#!/bin/bash
set -e

echo "Создаём пользователя репликации..."
psql -v ON_ERROR_STOP=1 --username "${POSTGRES_USER}" --dbname "postgres" <<-EOSQL
    CREATE USER ${REPLICATION_USER} WITH REPLICATION ENCRYPTED PASSWORD '${REPLICATION_PASSWORD}';
EOSQL

echo "Пользователь репликации '${REPLICATION_USER}' создан."