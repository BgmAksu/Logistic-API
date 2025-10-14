from dataclasses import dataclass
from datetime import datetime

from sqlalchemy.orm import Session

from .. import models
from ..errors import NotFoundError
from ..repositories.shipments import ShipmentRepository, SqlAlchemyShipmentRepository
from ..schemas import ShipmentIn


@dataclass
class ShipmentsService:
    """Business rules for shipments live here."""

    repo: ShipmentRepository = SqlAlchemyShipmentRepository()

    def create(self, db: Session, payload: ShipmentIn) -> models.Shipment:
        if not db.get(models.Address, payload.sender_address_id):
            raise NotFoundError("address", payload.sender_address_id)
        if not db.get(models.Address, payload.recipient_address_id):
            raise NotFoundError("address", payload.recipient_address_id)

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
        return self.repo.create(db, obj)

    def get(self, db: Session, shipment_id: int) -> models.Shipment | None:
        return self.repo.get(db, shipment_id)

    def list(self, db: Session, *, status: str | None, limit: int, offset: int):
        return self.repo.list(db, status=status, limit=limit, offset=offset)
