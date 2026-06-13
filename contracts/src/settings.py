from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    POSTGRES_HOST: str = "pg-master"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str

    POSTGRES_REPLICA_HOST: str = "pg-replica"

    # Connection pool
    DB_POOL_MIN_SIZE: int = 2
    DB_POOL_MAX_SIZE: int = 10

    # JWT (для будущих админских проверок)
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
