# Parcels: list and create for an existing shipment.

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy.orm import Session

from .. import schemas
from ..deps import get_db
from ..services.parcels import ParcelsService

router = APIRouter(prefix="/api/parcels", tags=["parcels"])
service = ParcelsService()


def pagination(
    limit: int = Query(50, ge=1, le=200, description="Page size (max 200)"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
):
    """Reusable pagination dependency."""
    return {"limit": limit, "offset": offset}


@router.post("", response_model=schemas.ParcelOut, status_code=201)
def create_parcel(payload: schemas.ParcelIn, db: Session = Depends(get_db)):
    return service.create(db, payload)


@router.get("", response_model=list[schemas.ParcelOut])
def list_parcels(
    shipment_id: int | None = Query(None),
    page: dict = Depends(pagination),
    db: Session = Depends(get_db),
):
    return service.list(db, shipment_id=shipment_id, **page)


@router.get("/{parcel_id}", response_model=schemas.ParcelOut)
def get_parcel(parcel_id: int = Path(..., ge=1), db: Session = Depends(get_db)):
    obj = service.get(db, parcel_id)
    if not obj:
        raise HTTPException(404, "parcel not found")
    return obj
