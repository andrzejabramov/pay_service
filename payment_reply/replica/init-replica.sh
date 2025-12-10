#!/bin/bash
set -e

# Ждём доступность мастера
echo "Ожидание запуска pg-master..."
until pg_isready -h pg-master -p 5432 -U "${POSTGRES_USER}"; do
  sleep 2
done

echo "Выполняем pg_basebackup с мастера..."

# Останавливаем PostgreSQL (если стартовал)
pg_ctl -D /var/lib/postgresql/data stop -m fast >/dev/null 2>&1 || true

# Очищаем данные
rm -rf /var/lib/postgresql/data/*

# Выполняем base backup
PGPASSWORD="${REPLICATION_PASSWORD}" pg_basebackup \
  -h pg-master \
  -U "${REPLICATION_USER}" \
  -D /var/lib/postgresql/data \
  -P \
  -v \
  -R

echo "Реплика инициализирована. Запуск PostgreSQL..."

# Передаём управление основному entrypoint'у
exec docker-entrypoint.sh postgres