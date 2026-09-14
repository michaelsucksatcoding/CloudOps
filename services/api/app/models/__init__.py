"""Database entity models."""

from services.api.app.database import Base
from services.api.app.models.service import ServiceEntity
from services.api.app.models.telemetry import TelemetryEntity

__all__ = ["Base", "ServiceEntity", "TelemetryEntity"]
