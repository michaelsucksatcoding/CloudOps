"""API Schemas exports."""

from services.api.app.schemas.analytics import AnalyticsSummaryResponse
from services.api.app.schemas.health import HealthResponse
from services.api.app.schemas.incident import IncidentResponse
from services.api.app.schemas.ml import AnomalyResponse, ServiceHealthResponse
from services.api.app.schemas.service import (
    ServiceBase,
    ServiceCreate,
    ServiceResponse,
    ServiceUpdate,
)
from services.api.app.schemas.telemetry import (
    TelemetryEventCreate,
    TelemetryEventResponse,
)

# Alias TelemetryEvent for compatibility
TelemetryEvent = TelemetryEventCreate

__all__ = [
    "AnalyticsSummaryResponse",
    "AnomalyResponse",
    "HealthResponse",
    "IncidentResponse",
    "ServiceBase",
    "ServiceCreate",
    "ServiceHealthResponse",
    "ServiceResponse",
    "ServiceUpdate",
    "TelemetryEvent",
    "TelemetryEventCreate",
    "TelemetryEventResponse",
]
