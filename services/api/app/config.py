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

    # Telemetry producer selection: "in_memory" for local testing, "kinesis" when
    # an explicit deployment intends to publish events to Kinesis Data Streams.
    telemetry_producer: str = "in_memory"

    # AWS configuration (for Kinesis, S3, DynamoDB)
    aws_region: str = "us-east-1"
    telemetry_stream_name: str = "cloudops-telemetry-stream"
    s3_data_lake_bucket: str = "cloudops-telemetry-lake"
    dynamodb_hot_table: str = "cloudops-telemetry-hot"


settings = Settings()
