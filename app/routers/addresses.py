# Minimal address endpoints so we can create addresses for shipments.

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from .. import models, schemas
from ..deps import get_db

router = APIRouter(prefix="/api/addresses", tags=["addresses"])

@router.post("", response_model=schemas.AddressOut, status_code=201)
def create_address(payload: schemas.AddressIn, db: Session = Depends(get_db)):
    obj = models.Address(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

@router.get("", response_model=list[schemas.AddressOut])
def list_addresses(db: Session = Depends(get_db)):
    return db.execute(select(models.Address)).scalars().all()