"""Incident response schemas."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class IncidentResponse(BaseModel):
    """Incident schema."""

    incident_id: str
    service_id: str
    title: str
    severity: str
    status: str
    created_at: datetime
    resolved_at: datetime | None = None
    details: dict[str, Any] = Field(default_factory=dict)
