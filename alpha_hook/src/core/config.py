from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # === Application ===
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    LOG_LEVEL: str = "INFO"
    ENVIRONMENT: str = "development"  # development | staging | production

    # === Database (через PgBouncer - write pool) ===
    DB_HOST: str = "pgbouncer"  # Или localhost для локальной разработки
    DB_PORT: int = 5432  # Внутренний порт PgBouncer
    DB_NAME: str = "newsportal"
    DB_USER: str = "app_user"
    DB_PASSWORD: str = "God1980obezyanj!"
    DB_POOL_MIN: int = 5
    DB_POOL_MAX: int = 20

    # === RabbitMQ (для асинхронных задач) ===
    RABBITMQ_HOST: str = "rabbitmq"
    RABBITMQ_PORT: int = 5672
    RABBITMQ_USER: str = "app_user"
    RABBITMQ_PASSWORD: str = "God1980obezyanj!"
    RABBITMQ_QUEUE_CALLBACK: str = "sbp_callback_queue"

    # === Alpha Bank ===
    ALPHA_BANK_WEBHOOK_SECRET: Optional[str] = None
    ALPHA_BANK_TEST_MODE: bool = True  # Отключает проверку подписи в dev

    # === External services ===
    CASH_REGISTER_WEBHOOK_URL: Optional[str] = None
    PRINCIPAL_CALLBACK_URL: Optional[str] = None

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()