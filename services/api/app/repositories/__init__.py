"""Repository interfaces and classes."""

from services.api.app.repositories.service import ServiceRepository
from services.api.app.repositories.telemetry import TelemetryRepository

__all__ = ["ServiceRepository", "TelemetryRepository"]
