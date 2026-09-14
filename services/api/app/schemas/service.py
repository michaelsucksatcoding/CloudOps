"""Service request and response schemas."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ServiceBase(BaseModel):
    """Base fields for a monitored service."""

    name: str = Field(
        ..., min_length=1, max_length=128, description="Display name of service"
    )
    environment: str = Field(
        default="dev", max_length=32, description="Target environment"
    )


class ServiceCreate(ServiceBase):
    """Payload to register a new monitored service."""

    id: str = Field(
        ..., min_length=1, max_length=64, description="Unique identifier for service"
    )


class ServiceUpdate(BaseModel):
    """Payload to update an existing service."""

    name: str | None = Field(default=None, min_length=1, max_length=128)
    environment: str | None = Field(default=None, max_length=32)
    status: str | None = Field(default=None, max_length=32)
    current_health_score: float | None = Field(default=None, ge=0.0, le=1.0)


class ServiceResponse(BaseModel):
    """Response schema for a monitored service."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    environment: str
    current_health_score: float
    status: str
    created_at: datetime
    updated_at: datetime
