# Tracking events ingestion & listing.


from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session

from .. import schemas
from ..deps import get_db
from ..services.tracking import TrackingService

router = APIRouter(prefix="/api/tracking-events", tags=["tracking"])
service = TrackingService()


@router.post("", response_model=schemas.TrackingEventOut, status_code=201)
def create_event(payload: schemas.TrackingEventIn, db: Session = Depends(get_db)):
    try:
        return service.create(db, payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get("/parcel/{parcel_id}", response_model=list[schemas.TrackingEventOut])
def list_events(parcel_id: int = Path(..., ge=1), db: Session = Depends(get_db)):
    return service.list_for_parcel(db, parcel_id)
