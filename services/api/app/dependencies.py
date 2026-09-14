"""Dependency injection providers."""

from fastapi import Depends
from sqlalchemy.orm import Session

from services.api.app.config import Settings, settings
from services.api.app.database import get_db
from services.api.app.repositories.service import ServiceRepository
from services.api.app.repositories.telemetry import TelemetryRepository
from services.event_processor.producer import TelemetryProducer, get_stream_producer
from services.event_processor.storage import HotStorage, get_hot_store


def get_settings() -> Settings:
    """Dependency provider for application configuration settings."""
    return settings


def get_service_repository(db: Session = Depends(get_db)) -> ServiceRepository:
    """Dependency provider for ServiceRepository."""
    return ServiceRepository(db)


def get_telemetry_repository(db: Session = Depends(get_db)) -> TelemetryRepository:
    """Dependency provider for TelemetryRepository."""
    return TelemetryRepository(db)


def get_producer() -> TelemetryProducer:
    """Dependency provider for streaming TelemetryProducer."""
    return get_stream_producer()


def get_hot_storage() -> HotStorage:
    """Dependency provider for realtime HotStorage."""
    return get_hot_store()
