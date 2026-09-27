# Event Processing Architecture

## Current path

```text
Client
  │  POST /events
  ▼
FastAPI  ──►  Pydantic validation
  │
  ├──►  PostgreSQL (durable system of record, created_at ordered)
  │
  └──►  InMemoryProducer (process-local observability buffer)
            │
            │  separate process
            ▼
      event-processor worker
        polls rows newer than a created_at watermark
            │
            ▼
      TelemetryProcessor
        ├──►  HotStorage   (recent events per service)
        └──►  DataLake     (partitioned JSON records)
            │
            ▼
      AnalyticsPipeline / ML feature engineering
```

The API persists an event **before** publishing it. The worker is therefore
never the sole holder of an accepted event, and no telemetry is lost if the
worker is down when ingestion happens.

### Why the worker polls the database

The API and the event processor are separate OS processes (separate containers
and, in Kubernetes, separate pods). The in-memory producer is process-local, so
it cannot hand events across that boundary. The worker therefore consumes the
durable PostgreSQL rows directly, using a `created_at` watermark for ordering and
at-least-once delivery.

`process_pending_events()` in `services/event_processor/handler.py` returns the
new watermark, and the rows themselves are never mutated or deleted.

### Failure handling

- A transient database or storage failure is logged with a full traceback and
  retried on the next poll; the worker never exits on a bad cycle.
- A malformed record fails in isolation: `TelemetryProcessor.process_batch()`
  records the error and continues, so one bad event cannot block the batch.
- The watermark only advances over rows that were actually read, so a failure
  does not silently skip events.

## Architectural limitation: loss of durable asynchronous fan-out

This section documents a genuine capability reduction. It is not an equivalent
substitution.

**What was removed.** The previous architecture inserted a durable managed stream
(Kinesis) and a serverless consumer (Lambda) between the API and processing:

```text
API → Kinesis (durable, partitioned, replayable) → Lambda → DynamoDB + S3
```

That path provided:

| Capability | Former stream | Current database polling |
|---|---|---|
| Durability | Stream retained and replayable | Rows retained in PostgreSQL |
| Partitioned ordering | Ordered per `service` key | Ordered by `created_at` |
| Delivery semantics | At-least-once with broker retries | At-least-once, retried by poll loop |
| Independent scaling | Lambda scaled separately | Single worker replica by default |
| Backpressure isolation | Broker absorbs burst load | Bounded by database and poll batch |
| Failure isolation | Consumer failure did not affect ingest | Ingest path unaffected; worker retries |

**What is genuinely weaker now.**

1. **Throughput is bounded by PostgreSQL.** There is no broker absorbing bursts.
   `POLL_BATCH_SIZE` is 100 rows and `POLL_INTERVAL_SECONDS` is 5, so sustained
   rates far above the tested load will grow the lag between ingestion and
   routing. The watermark makes this observable but does not remove it.
2. **The hot store is in-process and not durable.** `InMemoryHotStore` holds
   recent events in RAM, so `/events/hot` reflects only events routed by the
   worker currently running, and that history is lost on restart. The removed
   DynamoDB store was durable. PostgreSQL remains the durable record, so no
   telemetry is permanently lost — but the "hot" tier no longer survives a
   restart.
3. **Replay is a database query, not a stream reset.** Recovering the data-lake
   tier after a worker outage means querying PostgreSQL for the affected
   `created_at` range, not resetting a stream cursor.
4. **Single-writer throughput.** Scaling out requires sharding the poll, which
   is not implemented.

**What is unchanged.** Event validation, the `TelemetryProcessor` routing logic,
the hot/data-lake key format, the analytics feature pipeline, the ML model, and
all Prometheus metrics are untouched. Only the transport between the API and the
processor changed.

**Future option.** If measured throughput becomes a constraint, a local broker
such as Redis Streams (Redis is already an optional dependency) could restore
durable fan-out without reintroducing a cloud provider. This has not been
implemented because the current evaluation does not justify it — see
[ADR 0005](../decisions/0005-cloud-neutral-architecture.md).
