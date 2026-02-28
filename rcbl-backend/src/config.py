from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # ── Database ──────────────────────────────────────────────────────────────
    DATABASE_URL: str = "postgresql+asyncpg://rcbl_admin:rcbl_secret@localhost:5432/rcbl"

    # ── Redis ─────────────────────────────────────────────────────────────────
    REDIS_URL: str = "redis://localhost:6379/0"

    # ── JWT ───────────────────────────────────────────────────────────────────
    SECRET_KEY: str = "insecure-dev-key-replace-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ── S3 / MinIO ────────────────────────────────────────────────────────────
    S3_BUCKET: str = "rcbl-invoices"
    S3_ENDPOINT_URL: str = "http://localhost:9000"
    AWS_ACCESS_KEY_ID: str = "minioadmin"
    AWS_SECRET_ACCESS_KEY: str = "minioadmin"

    # ── OpenAI OCR ────────────────────────────────────────────────────────────
    OPENAI_API_KEY: str = "sk-placeholder"
    OCR_CONFIDENCE_THRESHOLD: float = 0.85

    # ── App ───────────────────────────────────────────────────────────────────
    ENVIRONMENT: str = "development"
    ALLOWED_ORIGINS: list[str] = ["http://localhost:3000"]

    # ── Observability ─────────────────────────────────────────────────────────
    OTLP_ENDPOINT: str = "http://localhost:4317"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
