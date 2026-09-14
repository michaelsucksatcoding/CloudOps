"""Services management endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status

from services.api.app.dependencies import get_service_repository
from services.api.app.repositories.service import ServiceRepository
from services.api.app.schemas.service import (
    ServiceCreate,
    ServiceResponse,
    ServiceUpdate,
)

router = APIRouter(prefix="/services", tags=["Services"])


@router.get("", response_model=list[ServiceResponse])
def list_services(
    skip: int = 0,
    limit: int = 100,
    repo: ServiceRepository = Depends(get_service_repository),
) -> list[ServiceResponse]:
    """List all registered services."""
    services = repo.list_all(skip=skip, limit=limit)
    return [ServiceResponse.model_validate(s) for s in services]


@router.post("", response_model=ServiceResponse, status_code=status.HTTP_201_CREATED)
def create_service(
    service_in: ServiceCreate,
    repo: ServiceRepository = Depends(get_service_repository),
) -> ServiceResponse:
    """Register a new service in the platform."""
    existing = repo.get_by_id(service_in.id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Service with id '{service_in.id}' already exists",
        )
    created = repo.create(service_in)
    return ServiceResponse.model_validate(created)


@router.get("/{service_id}", response_model=ServiceResponse)
def get_service(
    service_id: str,
    repo: ServiceRepository = Depends(get_service_repository),
) -> ServiceResponse:
    """Get service details by ID."""
    service = repo.get_by_id(service_id)
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Service with id '{service_id}' not found",
        )
    return ServiceResponse.model_validate(service)


@router.patch("/{service_id}", response_model=ServiceResponse)
def update_service(
    service_id: str,
    update_in: ServiceUpdate,
    repo: ServiceRepository = Depends(get_service_repository),
) -> ServiceResponse:
    """Update service metadata or status."""
    service = repo.get_by_id(service_id)
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Service with id '{service_id}' not found",
        )
    updated = repo.update(service, update_in)
    return ServiceResponse.model_validate(updated)
