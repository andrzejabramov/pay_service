FROM python:3.11-slim

WORKDIR /app

# Системные зависимости
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Python зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Код приложения
COPY src ./src

# Папка для логов
RUN mkdir -p /app/logs

EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]