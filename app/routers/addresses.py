# Minimal address endpoints so we can create addresses for shipments.

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy.orm import Session

from .. import schemas
from ..deps import get_db
from ..services.addresses import AddressesService

router = APIRouter(prefix="/api/addresses", tags=["addresses"])
service = AddressesService()


def pagination(
    limit: int = Query(50, ge=1, le=200, description="Page size (max 200)"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
):
    """Reusable pagination dependency."""
    return {"limit": limit, "offset": offset}


@router.post("", response_model=schemas.AddressOut, status_code=201)
def create_address(payload: schemas.AddressIn, db: Session = Depends(get_db)):
    return service.create(db, payload)


@router.get("", response_model=list[schemas.AddressOut])
def list_addresses(page: dict = Depends(pagination), db: Session = Depends(get_db)):
    return service.list(db, **page)


@router.get("/{address_id}", response_model=schemas.AddressOut)
def get_address(address_id: int = Path(..., ge=1), db: Session = Depends(get_db)):
    obj = service.get(db, address_id)
    if not obj:
        raise HTTPException(404, "address not found")
    return obj
