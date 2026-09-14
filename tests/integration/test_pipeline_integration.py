"""Integration tests connecting simulator, stream producer, Lambda processor, storage, and analytics."""

import base64
import json

from services.analytics.pipeline import AnalyticsPipeline
from services.event_processor.handler import lambda_handler
from services.event_processor.processor import TelemetryProcessor
from services.event_processor.producer import InMemoryProducer
from services.event_processor.storage import (
    InMemoryDataLakeStore,
    InMemoryHotStore,
)
from services.simulator.incidents import IncidentScenario
from services.simulator.telemetry import TelemetrySimulator


def test_full_event_driven_pipeline_integration() -> None:
    """Verify complete event pipeline flow:
    1. Simulator produces events
    2. Stream Producer buffers them
    3. Lambda processor decodes and validates batch
    4. Hot Storage (DynamoDB mock) and Data Lake (S3 mock) receive items
    5. Analytics ETL processes data lake records into feature matrix.
    """
    simulator = TelemetrySimulator(seed=123)
    producer = InMemoryProducer()
    hot_store = InMemoryHotStore()
    lake_store = InMemoryDataLakeStore()
    processor = TelemetryProcessor(hot_storage=hot_store, data_lake_storage=lake_store)
    analytics = AnalyticsPipeline()

    # Step 1: Simulator generates events
    simulated_events = [
        simulator.generate_event(
            service="payment-api", scenario=IncidentScenario.CPU_SPIKE
        )
        for _ in range(5)
    ]

    # Step 2: Stream producer publishes events
    producer.send_batch(simulated_events)
    buffered = producer.get_events()
    assert len(buffered) == 5

    # Step 3: Simulate Kinesis invoking Lambda with batched events
    kinesis_records = [
        {
            "kinesis": {
                "data": base64.b64encode(
                    json.dumps(b["payload"]).encode("utf-8")
                ).decode("utf-8")
            }
        }
        for b in buffered
    ]
    lambda_event = {"Records": kinesis_records}
    lambda_res = lambda_handler(lambda_event, None, processor=processor)

    assert lambda_res["statusCode"] == 200
    assert lambda_res["processed"] == 5
    assert lambda_res["failed"] == 0

    # Step 4: Verify Hot Storage has the 5 events
    hot_events = hot_store.get_latest_events("payment-api", limit=10)
    assert len(hot_events) == 5

    # Step 5: Verify Data Lake has stored partitioned objects
    lake_objects = lake_store.get_objects()
    assert len(lake_objects) == 5

    # Step 6: Process raw Data Lake archives in Analytics ETL
    raw_lake_payloads = [json.loads(p) for p in lake_objects.values()]
    feature_matrix = analytics.run_batch_pipeline(raw_lake_payloads)

    assert len(feature_matrix) == 5
    assert "cpu_percent" in feature_matrix.columns
    assert "latency_ms" in feature_matrix.columns
