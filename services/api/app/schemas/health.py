"""Health check response schemas."""

from datetime import datetime

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """System health status response schema."""

    status: str = Field(..., description="Overall service status (ok/degraded/error)")
    app: str = Field(..., description="Application name")
    version: str = Field(..., description="Application release version")
    environment: str = Field(..., description="Deployment environment")
    timestamp: datetime = Field(..., description="Current server time (UTC)")
    database: str = Field(default="connected", description="Database connection status")
