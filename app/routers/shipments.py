# Basic shipment CRUD: create, list, get.

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import models, schemas
from ..deps import get_db

router = APIRouter(prefix="/api/shipments", tags=["shipments"])


@router.post("", response_model=schemas.ShipmentOut, status_code=201)
def create_shipment(payload: schemas.ShipmentIn, db: Session = Depends(get_db)):
    # Ensure addresses exist
    if not db.get(models.Address, payload.sender_address_id):
        raise HTTPException(400, "sender_address_id does not exist")
    if not db.get(models.Address, payload.recipient_address_id):
        raise HTTPException(400, "recipient_address_id does not exist")

    obj = models.Shipment(
        reference=payload.reference,
        service_level=payload.service_level,
        status=payload.status,
        sender_address_id=payload.sender_address_id,
        recipient_address_id=payload.recipient_address_id,
        planned_delivery_date=payload.planned_delivery_date,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("", response_model=list[schemas.ShipmentOut])
def list_shipments(
    status: str | None = Query(None, description="Filter by status"),
    service_level: str | None = Query(None, description="Filter by service level"),
    db: Session = Depends(get_db),
):
    stmt = select(models.Shipment)
    if status:
        stmt = stmt.where(models.Shipment.status == status)
    if service_level:
        stmt = stmt.where(models.Shipment.service_level == service_level)
    return db.execute(stmt).scalars().all()


@router.get("/{shipment_id}", response_model=schemas.ShipmentOut)
def get_shipment(shipment_id: int, db: Session = Depends(get_db)):
    obj = db.get(models.Shipment, shipment_id)
    if not obj:
        raise HTTPException(404, "Shipment not found")
    return obj
