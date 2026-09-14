"""ML and health score schemas."""

from datetime import datetime

from pydantic import BaseModel, Field


class ServiceHealthResponse(BaseModel):
    """Service health score and status schema."""

    service_id: str
    status: str
    health_score: float = Field(..., ge=0.0, le=1.0)
    last_updated: datetime
    active_incidents: int = 0
    anomaly_count_last_hour: int = 0


class AnomalyResponse(BaseModel):
    """Anomaly detection result schema."""

    anomaly_id: str
    service_id: str
    timestamp: datetime
    anomaly_score: float
    is_anomaly: bool
    features: dict[str, float]
    root_cause_indicators: list[str] = Field(default_factory=list)
