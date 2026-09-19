"""Kinesis and In-Memory producer abstractions for streaming telemetry events."""

import json
import logging
import uuid
from threading import Lock
from typing import Any, Protocol

from services.api.app.config import settings
from services.api.app.schemas.telemetry import TelemetryEventCreate

logger = logging.getLogger(__name__)


class TelemetryProducer(Protocol):
    """Protocol for telemetry streaming producers."""

    def send_event(self, event: TelemetryEventCreate) -> str:
        """Send a single telemetry event to the stream. Returns sequence/record ID."""
        ...

    def send_batch(self, events: list[TelemetryEventCreate]) -> list[str]:
        """Send a batch of telemetry events to the stream. Returns list of record IDs."""
        ...


class InMemoryProducer:
    """Thread-safe in-memory stream producer for local testing and offline execution."""

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


class KinesisProducer:
    """AWS Kinesis Data Streams producer implementation."""

    def __init__(
        self,
        stream_name: str | None = None,
        region: str | None = None,
        endpoint_url: str | None = None,
    ) -> None:
        self.stream_name = stream_name or settings.telemetry_stream_name
        self.region = region or settings.aws_region
        self.endpoint_url = endpoint_url

        try:
            import boto3

            kwargs: dict[str, Any] = {"region_name": self.region}
            if self.endpoint_url:
                kwargs["endpoint_url"] = self.endpoint_url
            self._kinesis_client = boto3.client("kinesis", **kwargs)
        except Exception as err:
            logger.warning("Failed to initialize boto3 Kinesis client: %s", err)
            self._kinesis_client = None

    def send_event(self, event: TelemetryEventCreate) -> str:
        """Publish a single telemetry event to Kinesis Data Stream."""
        if self._kinesis_client is None:
            raise RuntimeError("Kinesis client is not initialized")

        payload = json.dumps(event.model_dump(mode="json"))
        partition_key = event.service

        response = self._kinesis_client.put_record(
            StreamName=self.stream_name,
            Data=payload.encode("utf-8"),
            PartitionKey=partition_key,
        )
        seq_num: str = response.get("SequenceNumber", str(uuid.uuid4()))
        logger.info(
            "Published event to Kinesis stream=%s partition_key=%s seq=%s",
            self.stream_name,
            partition_key,
            seq_num,
        )
        return seq_num

    def send_batch(self, events: list[TelemetryEventCreate]) -> list[str]:
        """Publish a batch of events to Kinesis via put_records."""
        if self._kinesis_client is None:
            raise RuntimeError("Kinesis client is not initialized")
        if not events:
            return []

        records = [
            {
                "Data": json.dumps(e.model_dump(mode="json")).encode("utf-8"),
                "PartitionKey": e.service,
            }
            for e in events
        ]

        response = self._kinesis_client.put_records(
            StreamName=self.stream_name,
            Records=records,
        )
        results: list[str] = [
            r.get("SequenceNumber", str(uuid.uuid4()))
            for r in response.get("Records", [])
        ]
        return results


# Global in-memory producer for local runs
_default_producer = InMemoryProducer()

# Lazily-created Kinesis producer for deployments that explicitly opt in.
_kinesis_producer: KinesisProducer | None = None


def get_stream_producer() -> TelemetryProducer:
    """Dependency / factory provider for TelemetryProducer.

    Returns an in-memory producer by default (safe for local testing and
    offline execution). When ``TELEMETRY_PRODUCER=kinesis`` is set explicitly,
    returns the Kinesis Data Streams producer backed by the configured stream.
    """
    if settings.telemetry_producer.lower() == "kinesis":
        global _kinesis_producer
        if _kinesis_producer is None:
            _kinesis_producer = KinesisProducer()
        return _kinesis_producer
    return _default_producer
