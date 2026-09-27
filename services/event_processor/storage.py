"""Hot storage and data lake storage abstractions for telemetry events."""

import json
import logging
import uuid
from threading import Lock
from typing import Protocol

from services.api.app.schemas.telemetry import TelemetryEventCreate

logger = logging.getLogger(__name__)


class HotStorage(Protocol):
    """Protocol for hot/realtime telemetry storage."""

    def put_event(self, event: TelemetryEventCreate) -> None:
        """Store or update a telemetry event in hot storage."""
        ...

    def get_latest_events(
        self, service: str, limit: int = 50
    ) -> list[TelemetryEventCreate]:
        """Retrieve recent telemetry events for a specific service."""
        ...

    def get_event(
        self, service: str, timestamp_iso: str
    ) -> TelemetryEventCreate | None:
        """Retrieve a specific telemetry event by partition and sort key."""
        ...


class InMemoryHotStore:
    """Thread-safe in-memory hot storage implementation."""

    def __init__(self) -> None:
        self._lock = Lock()
        # Key: service -> dict of timestamp_iso -> TelemetryEventCreate
        self._store: dict[str, dict[str, TelemetryEventCreate]] = {}

    def put_event(self, event: TelemetryEventCreate) -> None:
        """Store event in memory."""
        with self._lock:
            service_events = self._store.setdefault(event.service, {})
            service_events[event.timestamp.isoformat()] = event
            logger.debug(
                "Stored event in memory hot store: service=%s timestamp=%s",
                event.service,
                event.timestamp.isoformat(),
            )

    def get_latest_events(
        self, service: str, limit: int = 50
    ) -> list[TelemetryEventCreate]:
        """Get latest events ordered by timestamp descending."""
        with self._lock:
            service_events = self._store.get(service, {})
            sorted_events = sorted(
                service_events.values(),
                key=lambda e: e.timestamp,
                reverse=True,
            )
            return sorted_events[:limit]

    def get_event(
        self, service: str, timestamp_iso: str
    ) -> TelemetryEventCreate | None:
        """Get single event by service and ISO timestamp."""
        with self._lock:
            return self._store.get(service, {}).get(timestamp_iso)

    def clear(self) -> None:
        """Clear all stored events."""
        with self._lock:
            self._store.clear()


class DataLakeStorage(Protocol):
    """Protocol for cold data lake archival."""

    def save_event(self, event: TelemetryEventCreate) -> str:
        """Save telemetry event payload to data lake storage."""
        ...


class InMemoryDataLakeStore:
    """Thread-safe in-memory sink for data lake archives."""

    def __init__(self) -> None:
        self._lock = Lock()
        self._objects: dict[str, str] = {}

    def save_event(self, event: TelemetryEventCreate) -> str:
        """Store event as serialized JSON with a partitioned key."""
        dt = event.timestamp
        unique_id = uuid.uuid4().hex[:8]
        key = (
            f"year={dt.year:04d}/month={dt.month:02d}/day={dt.day:02d}/"
            f"service={event.service}/{event.service}_{dt.strftime('%Y%m%d%H%M%S%f')}_{unique_id}.json"
        )
        payload = json.dumps(event.model_dump(mode="json"))
        with self._lock:
            self._objects[key] = payload
        return key

    def get_objects(self) -> dict[str, str]:
        """Retrieve stored objects."""
        with self._lock:
            return dict(self._objects)

    def clear(self) -> None:
        """Clear all stored objects."""
        with self._lock:
            self._objects.clear()


# Global singleton in-memory stores for local execution
_default_hot_store = InMemoryHotStore()
_default_data_lake_store = InMemoryDataLakeStore()


def get_hot_store() -> HotStorage:
    """Factory provider for HotStorage."""
    return _default_hot_store


def get_data_lake_store() -> DataLakeStorage:
    """Factory provider for DataLakeStorage."""
    return _default_data_lake_store
