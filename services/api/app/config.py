"""Application configuration settings."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    app_name: str = "CloudOps AI"
    app_version: str = "0.1.0"
    environment: str = "dev"
    debug: bool = False
    log_level: str = "INFO"

    # Database
    database_url: str = (
        "postgresql://cloudops:cloudops_dev_pass@localhost:5432/cloudops_db"
    )

    # Optional Redis
    redis_url: str = "redis://localhost:6379/0"


settings = Settings()
