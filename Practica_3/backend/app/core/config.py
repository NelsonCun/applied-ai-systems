from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    project_name: str = "SmartInvoice"
    environment: str = "development"
    api_v1_prefix: str = "/api/v1"

    secret_key: str = "change-this-secret-key"
    access_token_expire_minutes: int = 480

    database_url: str = (
        "postgresql://smartinvoice_user:"
        "smartinvoice_password@db:5432/smartinvoice"
    )

    redis_url: str = "redis://redis:6379/0"
    celery_broker_url: str = "redis://redis:6379/0"
    celery_result_backend: str = "redis://redis:6379/1"

    cors_origins: str = "http://localhost:5173,http://localhost:8080"

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
        case_sensitive=False,
    )

    @property
    def cors_origin_list(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.cors_origins.split(",")
            if origin.strip()
        ]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
