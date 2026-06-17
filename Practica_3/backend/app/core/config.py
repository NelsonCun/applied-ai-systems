from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    project_name: str = "SmartInvoice"
    environment: str = "development"
    api_v1_prefix: str = "/api/v1"

    secret_key: str = "change-this-secret-key"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 480

    upload_dir: str = "/app/storage/uploads"
    max_upload_size_mb: int = 15

    processed_dir: str = "/app/storage/processed"
    reports_dir: str = "/app/storage/reports"

    rpa_target_url: str = "http://rpa-target:8080"
    rpa_username: str = "robot"
    rpa_password: str = "robot123"
    rpa_evidence_dir: str = "/app/storage/rpa"
    tesseract_language: str = "spa+eng"
    ocr_min_confidence: float = 60
    ocr_dpi: int = 300
    max_pdf_pages: int = 5

    database_url: str = (
        "postgresql://smartinvoice_user:"
        "smartinvoice_password@db:5432/smartinvoice"
    )

    redis_url: str = "redis://redis:6379/0"
    celery_broker_url: str = "redis://redis:6379/0"
    celery_result_backend: str = "redis://redis:6379/1"

    cors_origins: str = (
        "http://localhost:5174,"
        "http://localhost:8080"
    )

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
