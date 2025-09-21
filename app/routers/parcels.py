# Parcels: list and create for an existing shipment.

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from .. import models, schemas
from ..deps import get_db

router = APIRouter(prefix="/api/parcels", tags=["parcels"])

@router.get("", response_model=list[schemas.ParcelOut])
def list_parcels(db: Session = Depends(get_db)):
    return db.execute(select(models.Parcel)).scalars().all()

@router.post("", response_model=schemas.ParcelOut, status_code=201)
def create_parcel(payload: schemas.ParcelIn, db: Session = Depends(get_db)):
    if not db.get(models.Shipment, payload.shipment_id):
        raise HTTPException(400, "shipment_id does not exist")
    obj = models.Parcel(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj