"""Hot storage and Data Lake storage abstractions for telemetry events."""

import json
import logging
import uuid
from decimal import Decimal
from threading import Lock
from typing import Any, Protocol

from services.api.app.config import settings
from services.api.app.schemas.telemetry import TelemetryEventCreate

logger = logging.getLogger(__name__)


def _convert_floats_to_decimals(obj: Any) -> Any:
    """Recursively convert float values to Decimal for DynamoDB serialization."""
    if isinstance(obj, float):
        return Decimal(str(obj))
    if isinstance(obj, dict):
        return {k: _convert_floats_to_decimals(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_convert_floats_to_decimals(i) for i in obj]
    return obj


def _convert_decimals_to_floats(obj: Any) -> Any:
    """Recursively convert Decimal values back to float/int."""
    if isinstance(obj, Decimal):
        return float(obj) if obj % 1 != 0 else int(obj)
    if isinstance(obj, dict):
        return {k: _convert_decimals_to_floats(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_convert_decimals_to_floats(i) for i in obj]
    return obj


class HotStorage(Protocol):
    """Protocol for hot/realtime telemetry storage (DynamoDB / In-Memory)."""

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
    """Thread-safe in-memory hot storage implementation for local development and testing."""

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


class DynamoDBHotStore:
    """DynamoDB implementation of HotStorage."""

    def __init__(
        self,
        table_name: str | None = None,
        region: str | None = None,
        endpoint_url: str | None = None,
    ) -> None:
        self.table_name = table_name or settings.dynamodb_hot_table
        self.region = region or settings.aws_region
        self.endpoint_url = endpoint_url

        try:
            import boto3

            kwargs: dict[str, Any] = {"region_name": self.region}
            if self.endpoint_url:
                kwargs["endpoint_url"] = self.endpoint_url
            self._dynamodb = boto3.resource("dynamodb", **kwargs)
            self._table = self._dynamodb.Table(self.table_name)
        except Exception as err:
            logger.warning("Failed to initialize boto3 DynamoDB resource: %s", err)
            self._dynamodb = None
            self._table = None

    def put_event(self, event: TelemetryEventCreate) -> None:
        """Store telemetry event in DynamoDB table."""
        if self._table is None:
            raise RuntimeError("DynamoDB table resource is not initialized")

        item_dict = event.model_dump(mode="json")
        item_dict["timestamp_iso"] = event.timestamp.isoformat()
        dynamo_item = _convert_floats_to_decimals(item_dict)

        self._table.put_item(Item=dynamo_item)
        logger.debug(
            "Saved event to DynamoDB table %s: service=%s",
            self.table_name,
            event.service,
        )

    def get_latest_events(
        self, service: str, limit: int = 50
    ) -> list[TelemetryEventCreate]:
        """Query latest events by service partition key from DynamoDB."""
        if self._table is None:
            raise RuntimeError("DynamoDB table resource is not initialized")

        from boto3.dynamodb.conditions import Key

        response = self._table.query(
            KeyConditionExpression=Key("service").eq(service),
            ScanIndexForward=False,  # Descending order by sort key
            Limit=limit,
        )
        items = response.get("Items", [])
        return [
            TelemetryEventCreate.model_validate(_convert_decimals_to_floats(item))
            for item in items
        ]

    def get_event(
        self, service: str, timestamp_iso: str
    ) -> TelemetryEventCreate | None:
        """Get item by primary key (service, timestamp)."""
        if self._table is None:
            raise RuntimeError("DynamoDB table resource is not initialized")

        response = self._table.get_item(
            Key={"service": service, "timestamp": timestamp_iso}
        )
        item = response.get("Item")
        if not item:
            return None
        return TelemetryEventCreate.model_validate(_convert_decimals_to_floats(item))


class DataLakeStorage(Protocol):
    """Protocol for S3 cold storage / data lake archival."""

    def save_event(self, event: TelemetryEventCreate) -> str:
        """Save telemetry event payload to data lake storage."""
        ...


class InMemoryDataLakeStore:
    """Thread-safe in-memory sink for Data Lake archives."""

    def __init__(self) -> None:
        self._lock = Lock()
        self._objects: dict[str, str] = {}

    def save_event(self, event: TelemetryEventCreate) -> str:
        """Store event as serialized JSON with partition key."""
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


class S3DataLakeStore:
    """S3 implementation of DataLakeStorage."""

    def __init__(
        self,
        bucket_name: str | None = None,
        region: str | None = None,
        endpoint_url: str | None = None,
    ) -> None:
        self.bucket_name = bucket_name or settings.s3_data_lake_bucket
        self.region = region or settings.aws_region
        self.endpoint_url = endpoint_url

        try:
            import boto3

            kwargs: dict[str, Any] = {"region_name": self.region}
            if self.endpoint_url:
                kwargs["endpoint_url"] = self.endpoint_url
            self._s3_client = boto3.client("s3", **kwargs)
        except Exception as err:
            logger.warning("Failed to initialize boto3 S3 client: %s", err)
            self._s3_client = None

    def save_event(self, event: TelemetryEventCreate) -> str:
        """Save telemetry event as a JSON object in S3."""
        if self._s3_client is None:
            raise RuntimeError("S3 client is not initialized")

        dt = event.timestamp
        key = (
            f"telemetry/year={dt.year:04d}/month={dt.month:02d}/day={dt.day:02d}/"
            f"service={event.service}/{event.service}_{dt.strftime('%Y%m%d%H%M%S')}_{int(dt.timestamp() * 1000)}.json"
        )
        payload = json.dumps(event.model_dump(mode="json"))

        self._s3_client.put_object(
            Bucket=self.bucket_name,
            Key=key,
            Body=payload.encode("utf-8"),
            ContentType="application/json",
        )
        return key


# Global singleton in-memory stores for local execution
_default_hot_store = InMemoryHotStore()
_default_data_lake_store = InMemoryDataLakeStore()


def get_hot_store() -> HotStorage:
    """Factory provider for HotStorage."""
    return _default_hot_store


def get_data_lake_store() -> DataLakeStorage:
    """Factory provider for DataLakeStorage."""
    return _default_data_lake_store
