# Tracking events ingestion & listing.

from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import select
from ..deps import get_db
from .. import models, schemas

router = APIRouter(prefix="/api/tracking-events", tags=["tracking"])

@router.post("", response_model=schemas.TrackingEventOut, status_code=201)
def create_event(payload: schemas.TrackingEventIn, db: Session = Depends(get_db)):
    # Ensure parcel exists
    parcel = db.get(models.Parcel, payload.parcel_id)
    if not parcel:
        raise HTTPException(status_code=404, detail="Parcel not found")

    ev = models.TrackingEvent(
        parcel_id=payload.parcel_id,
        code=payload.code,
        description=payload.description,
        event_time=payload.event_time or datetime.utcnow(),
        lat=payload.lat,
        lon=payload.lon,
        location_name=payload.location_name,
    )
    db.add(ev)

    # If the event is DELIVERED, mark shipment as delivered
    if payload.code.upper() == "DELIVERED":
        shp = parcel.shipment
        shp.status = "DELIVERED"
        shp.delivered_at = ev.event_time

    db.commit()
    db.refresh(ev)
    return ev

@router.get("", response_model=list[schemas.TrackingEventOut])
def list_events(
    parcel_id: int | None = Query(default=None, description="Filter by parcel_id"),
    db: Session = Depends(get_db),
):
    stmt = select(models.TrackingEvent)
    if parcel_id is not None:
        stmt = stmt.where(models.TrackingEvent.parcel_id == parcel_id)
    return db.execute(stmt).scalars().all()
