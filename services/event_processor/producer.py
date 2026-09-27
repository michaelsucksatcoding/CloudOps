"""In-process telemetry producer abstraction for the local event pipeline."""

import logging
import uuid
from threading import Lock
from typing import Any, Protocol

from services.api.app.schemas.telemetry import TelemetryEventCreate

logger = logging.getLogger(__name__)


class TelemetryProducer(Protocol):
    """Protocol for telemetry producers."""

    def send_event(self, event: TelemetryEventCreate) -> str:
        """Send a single telemetry event. Returns the record ID."""
        ...

    def send_batch(self, events: list[TelemetryEventCreate]) -> list[str]:
        """Send a batch of telemetry events. Returns a list of record IDs."""
        ...


class InMemoryProducer:
    """Thread-safe in-memory producer for local and Kubernetes execution."""

    def __init__(self) -> None:
        self._lock = Lock()
        self._events: list[dict[str, Any]] = []

    def send_event(self, event: TelemetryEventCreate) -> str:
        """Buffer a single event in memory."""
        record_id = f"mem-rec-{uuid.uuid4()}"
        with self._lock:
            self._events.append(
                {
                    "record_id": record_id,
                    "event": event,
                    "payload": event.model_dump(mode="json"),
                }
            )
        logger.debug(
            "Produced event to in-memory stream: record_id=%s service=%s",
            record_id,
            event.service,
        )
        return record_id

    def send_batch(self, events: list[TelemetryEventCreate]) -> list[str]:
        """Buffer multiple events in memory."""
        return [self.send_event(e) for e in events]

    def get_events(self) -> list[dict[str, Any]]:
        """Retrieve all buffered events."""
        with self._lock:
            return list(self._events)

    def clear(self) -> None:
        """Clear buffered events."""
        with self._lock:
            self._events.clear()


# Global in-memory producer shared by the API process.
_default_producer = InMemoryProducer()


def get_stream_producer() -> TelemetryProducer:
    """Dependency / factory provider for TelemetryProducer.

    Returns the shared in-memory producer. The API persists every accepted
    event to PostgreSQL before publishing it here, so the in-process buffer is
    an observability aid rather than the durable system of record.
    """
    return _default_producer
