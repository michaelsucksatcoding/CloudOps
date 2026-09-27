"""Integration tests connecting simulator, producer, processor, storage, and analytics."""

import json

from services.analytics.pipeline import AnalyticsPipeline
from services.event_processor.processor import TelemetryProcessor
from services.event_processor.producer import InMemoryProducer
from services.event_processor.storage import (
    InMemoryDataLakeStore,
    InMemoryHotStore,
)
from services.simulator.incidents import IncidentScenario
from services.simulator.telemetry import TelemetrySimulator


def test_full_event_driven_pipeline_integration() -> None:
    """Verify the complete telemetry pipeline flow:
    1. Simulator produces events
    2. In-memory producer buffers them
    3. Processor validates and routes a batch of raw payloads
    4. Hot Storage and Data Lake receive the items
    5. Analytics ETL processes data lake records into a feature matrix.
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

    # Step 2: Producer publishes events
    producer.send_batch(simulated_events)
    buffered = producer.get_events()
    assert len(buffered) == 5

    # Step 3: Processor validates and routes the buffered payloads
    batch_result = processor.process_batch([b["payload"] for b in buffered])

    assert batch_result["processed"] == 5
    assert batch_result["failed"] == 0

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
