"""Service repository implementation using SQLAlchemy."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from services.api.app.models.service import ServiceEntity
from services.api.app.schemas.service import ServiceCreate, ServiceUpdate


class ServiceRepository:
    """Repository handling database operations for monitored services."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, service_id: str) -> ServiceEntity | None:
        """Fetch a service by its ID."""
        stmt = select(ServiceEntity).where(ServiceEntity.id == service_id)
        return self.db.scalars(stmt).first()

    def list_all(self, skip: int = 0, limit: int = 100) -> list[ServiceEntity]:
        """List all services with pagination."""
        stmt = select(ServiceEntity).offset(skip).limit(limit)
        return list(self.db.scalars(stmt).all())

    def create(self, service_in: ServiceCreate) -> ServiceEntity:
        """Create and persist a new service."""
        service = ServiceEntity(
            id=service_in.id,
            name=service_in.name,
            environment=service_in.environment,
            status="healthy",
            current_health_score=1.0,
        )
        self.db.add(service)
        self.db.commit()
        self.db.refresh(service)
        return service

    def update(self, service: ServiceEntity, update_in: ServiceUpdate) -> ServiceEntity:
        """Update an existing service."""
        update_data = update_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(service, field, value)
        self.db.commit()
        self.db.refresh(service)
        return service
