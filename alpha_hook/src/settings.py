# alpha_hook/src/settings.py
from pydantic_settings import BaseSettings
from pydantic import ConfigDict, PostgresDsn, AmqpDsn
from pathlib import Path
from typing import Optional


class Settings(BaseSettings):
    """
    Настройки приложения.

    ВАЖНО: Секреты (пароли, ключи) НЕ имеют значений по умолчанию.
    Они должны передаваться ТОЛЬКО через переменные окружения или .env файл.
    """

    # === PostgreSQL компоненты (загружаются из корневого .env) ===
    postgres_user: str  # Обязательное, без дефолта!
    postgres_password: str  # Обязательное, без дефолта!
    postgres_db: str  # Обязательное, без дефолта!

    app_reader_user: str  # Обязательное
    app_reader_password: str  # Обязательное
    postgres_replica_host: str = "pg-replica"
    postgres_replica_port: str = "5432"

    # Хосты и порты (внутри Docker — всегда pg-master:5432)
    postgres_host: str = "pg-master"
    postgres_port: str = "5432"

    # === RabbitMQ компоненты ===
    rabbitmq_default_user: str
    rabbitmq_default_pass: str
    rabbitmq_host: str = "rabbitmq"
    rabbitmq_port: str = "5672"

    # === Alpha Bank (публичные настройки) ===
    alpha_bank_test_mode: bool = True

    # === Секреты Альфа-Банка (ТОЛЬКО из окружения!) ===
    # None = ключ не настроен, валидация checksum пропускается
    alpha_bank_webhook_secret: Optional[str] = None

    # === Логирование ===
    # /app/logs — путь внутри контейнера (проброшен на хост через volume)
    log_dir: Path = Path("/app/logs")

    # === Строгая валидация ===
    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",  # Запретить необъявленные переменные
    )

    # === Производные свойства (не загружаются из env, собираются в коде) ===

    @property
    def database_write_url(self) -> PostgresDsn:
        """DSN для записи (мастер)"""
        return PostgresDsn.build(
            scheme="postgresql",
            username=self.postgres_user,
            password=self.postgres_password,
            host=self.postgres_host,
            port=int(self.postgres_port),
            path=self.postgres_db,
        )

    @property
    def database_read_url(self) -> PostgresDsn:
        """DSN для чтения (реплика)"""
        return PostgresDsn.build(
            scheme="postgresql",
            username=self.app_reader_user,
            password=self.app_reader_password,
            host=self.postgres_host,
            port=int(self.postgres_port),
            path=self.postgres_db,
        )

    @property
    def rabbitmq_url(self) -> AmqpDsn:
        """DSN для RabbitMQ"""
        return AmqpDsn.build(
            scheme="amqp",
            username=self.rabbitmq_default_user,
            password=self.rabbitmq_default_pass,
            host=self.rabbitmq_host,
            port=int(self.rabbitmq_port),
            path="/",
        )


settings = Settings()