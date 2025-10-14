# Basic shipment CRUD: create, list, get.


from fastapi import APIRouter, Depends, HTTPException, Path, Query, Request
from sqlalchemy.orm import Session

from .. import schemas
from ..deps import get_db
from ..limits import limiter
from ..services.shipments import ShipmentsService

router = APIRouter(prefix="/api/shipments", tags=["shipments"])
service = ShipmentsService()


def pagination(
    limit: int = Query(50, ge=1, le=200, description="Page size (max 200)"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
):
    """Reusable pagination dependency."""
    return {"limit": limit, "offset": offset}


@router.post("", response_model=schemas.ShipmentOut, status_code=201)
def create_shipment(payload: schemas.ShipmentIn, db: Session = Depends(get_db)):
    return service.create(db, payload)


@router.get("", response_model=list[schemas.ShipmentOut])
@limiter.limit("2/minute")  # demo throttle
def list_shipments(
    request: Request,
    status: str | None = Query(None, description="Filter by shipment status"),
    page: dict = Depends(pagination),
    db: Session = Depends(get_db),
):
    return service.list(db, status=status, **page)


@router.get("/{shipment_id}", response_model=schemas.ShipmentOut)
def get_shipment(
    shipment_id: int = Path(..., ge=1, description="Shipment primary key"),
    db: Session = Depends(get_db),
):
    """Return a single shipment by id or 404 if not found."""
    obj = service.get(db, shipment_id)
    if not obj:
        raise HTTPException(status_code=404, detail="shipment not found")
    return obj
