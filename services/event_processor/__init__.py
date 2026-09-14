"""Event processor package for telemetry ingestion, streaming, and storage."""

from services.event_processor.handler import lambda_handler
from services.event_processor.processor import TelemetryProcessor
from services.event_processor.producer import (
    InMemoryProducer,
    KinesisProducer,
    TelemetryProducer,
    get_stream_producer,
)
from services.event_processor.storage import (
    DataLakeStorage,
    DynamoDBHotStore,
    HotStorage,
    InMemoryDataLakeStore,
    InMemoryHotStore,
    S3DataLakeStore,
    get_data_lake_store,
    get_hot_store,
)

__all__ = [
    "DataLakeStorage",
    "DynamoDBHotStore",
    "HotStorage",
    "InMemoryDataLakeStore",
    "InMemoryHotStore",
    "InMemoryProducer",
    "KinesisProducer",
    "S3DataLakeStore",
    "TelemetryProcessor",
    "TelemetryProducer",
    "get_data_lake_store",
    "get_hot_store",
    "get_stream_producer",
    "lambda_handler",
]
