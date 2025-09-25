# Minimal address endpoints so we can create addresses for shipments.

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select, text
from .. import models, schemas
from ..deps import get_db

router = APIRouter(prefix="/api/addresses", tags=["addresses"])

@router.post("", response_model=schemas.AddressOut, status_code=201)
def create_address(payload: schemas.AddressIn, db: Session = Depends(get_db)):
    obj = models.Address(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    if obj.lat is not None and obj.lon is not None:
        db.execute(
            text("UPDATE addresses SET geom = ST_SetSRID(ST_MakePoint(:lon, :lat), 4326) WHERE id = :id"),
            {"lon": obj.lon, "lat": obj.lat, "id": obj.id},
        )
        db.commit()
    return obj

@router.get("", response_model=list[schemas.AddressOut])
def list_addresses(db: Session = Depends(get_db)):
    return db.execute(select(models.Address)).scalars().all()