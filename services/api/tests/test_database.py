"""Direct database repository tests."""

from datetime import UTC, datetime

from sqlalchemy.orm import Session

from services.api.app.repositories.service import ServiceRepository
from services.api.app.repositories.telemetry import TelemetryRepository
from services.api.app.schemas.service import ServiceCreate, ServiceUpdate
from services.api.app.schemas.telemetry import TelemetryEventCreate


def test_service_repository_crud(db_session: Session) -> None:
    """Verify ServiceRepository database CRUD operations."""
    repo = ServiceRepository(db_session)

    # Create
    service_in = ServiceCreate(id="db-svc", name="Database Service", environment="dev")
    service = repo.create(service_in)
    assert service.id == "db-svc"
    assert service.name == "Database Service"

    # Get
    fetched = repo.get_by_id("db-svc")
    assert fetched is not None
    assert fetched.id == "db-svc"

    # Update
    updated = repo.update(
        fetched, ServiceUpdate(name="Updated DB Service", current_health_score=0.9)
    )
    assert updated.name == "Updated DB Service"
    assert updated.current_health_score == 0.9

    # List
    all_services = repo.list_all()
    assert any(s.id == "db-svc" for s in all_services)


def test_telemetry_repository_crud(db_session: Session) -> None:
    """Verify TelemetryRepository database CRUD operations."""
    repo = TelemetryRepository(db_session)

    event_in = TelemetryEventCreate(
        timestamp=datetime.now(UTC),
        service="db-telemetry-svc",
        endpoint="/test",
        status_code=200,
        latency_ms=50.0,
        cpu_percent=25.0,
        memory_percent=35.0,
    )
    event = repo.create(event_in)
    assert event.id is not None
    assert event.service == "db-telemetry-svc"

    # List by service
    events = repo.list_by_service("db-telemetry-svc")
    assert len(events) >= 1
    assert events[0].endpoint == "/test"
