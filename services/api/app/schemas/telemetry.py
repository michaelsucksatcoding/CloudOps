"""Telemetry event schemas."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TelemetryEventCreate(BaseModel):
    """Payload to ingest a telemetry event."""

    timestamp: datetime = Field(..., description="Event timestamp (ISO 8601)")
    service: str = Field(..., min_length=1, max_length=64, description="Service name")
    endpoint: str = Field(..., min_length=1, max_length=255, description="API endpoint")
    status_code: int = Field(..., ge=100, le=599, description="HTTP status code")
    latency_ms: float = Field(..., ge=0.0, description="Latency in milliseconds")
    cpu_percent: float = Field(..., ge=0.0, le=100.0, description="CPU percent usage")
    memory_percent: float = Field(
        ..., ge=0.0, le=100.0, description="Memory percent usage"
    )
    request_rate: float | None = Field(
        default=None, ge=0.0, description="Requests per second"
    )
    queue_depth: int | None = Field(default=None, ge=0, description="Queue depth count")
    deployment_version: str | None = Field(default=None, max_length=64)
    instance_id: str | None = Field(default=None, max_length=64)
    environment: str | None = Field(default="dev", max_length=32)
    tenant_id: str | None = Field(default=None, max_length=64)
    region: str | None = Field(default="us-east-1", max_length=32)


class TelemetryEventResponse(TelemetryEventCreate):
    """Response schema for a stored telemetry event."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    created_at: datetime
