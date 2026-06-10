FROM python:3.11-slim

WORKDIR /app

# Системные зависимости
# gcc нужен для сборки wheels (cryptography/asyncpg), curl можно убрать если не используется в логике
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Python зависимости (слой кешируется, пока не изменится requirements.txt)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Код + тестовый скрипт
COPY src/ ./src/
COPY test_sbp_getqrcd.py .

# Папка для логов
RUN mkdir -p /app/logs

EXPOSE 8000
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]