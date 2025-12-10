#!/bin/bash
set -e

# Загружаем .env
export $(grep -v '^#' .env | xargs)

# Указываем БД — можно тоже вынести в .env, но у тебя она совпадает с POSTGRES_DB
DB_NAME="${POSTGRES_DB:-payments}"  # fallback на payments, если не задано

# Путь к шаблону
TEMPLATE="./sql/post-init/01_create_app_users.sql.template"
OUTPUT="./sql/post-init/01_create_app_users.sql"

# Подставляем переменные
envsubst < "$TEMPLATE" > "$OUTPUT"

# Копируем в контейнер и выполняем
echo "Разворачиваем пользователя ${APP_READER_USER} в БД ${DB_NAME}..."
docker cp "$OUTPUT" pg-master:/tmp/app_users.sql
docker exec pg-master psql -U "${POSTGRES_USER}" -d "$DB_NAME" -f /tmp/app_users.sql

echo "Готово ✅"