"""Incidents endpoints."""

from datetime import UTC, datetime

from fastapi import APIRouter, HTTPException, status

from services.api.app.schemas import IncidentResponse

router = APIRouter()


@router.get("/incidents", response_model=list[IncidentResponse])
def list_incidents(service_id: str | None = None) -> list[IncidentResponse]:
    """List operational incidents."""
    return []


@router.get("/incidents/{incident_id}", response_model=IncidentResponse)
def get_incident(incident_id: str) -> IncidentResponse:
    """Get incident details by incident ID."""
    if incident_id == "not-found":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Incident {incident_id} not found",
        )
    return IncidentResponse(
        incident_id=incident_id,
        service_id="payment-api",
        title="Simulated Latency Spike",
        severity="medium",
        status="resolved",
        created_at=datetime.now(UTC),
        resolved_at=datetime.now(UTC),
        details={"scenario": "latency_spike"},
    )
