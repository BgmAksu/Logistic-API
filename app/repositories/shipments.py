from collections.abc import Sequence
from typing import Protocol

from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import models


class ShipmentRepository(Protocol):
    """Abstraction for persistence (Dependency Inversion)."""

    def create(self, db: Session, obj: models.Shipment) -> models.Shipment: ...
    def get(self, db: Session, shipment_id: int) -> models.Shipment | None: ...
    def list(
        self, db: Session, *, status: str | None, limit: int, offset: int
    ) -> Sequence[models.Shipment]: ...


class SqlAlchemyShipmentRepository:
    """SQLAlchemy-backed repository."""

    def create(self, db: Session, obj: models.Shipment) -> models.Shipment:
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj

    def get(self, db: Session, shipment_id: int) -> models.Shipment | None:
        return db.get(models.Shipment, shipment_id)

    def list(self, db: Session, *, status: str | None, limit: int, offset: int):
        stmt = select(models.Shipment).limit(limit).offset(offset)
        if status:
            stmt = stmt.where(models.Shipment.status == status)
        return db.execute(stmt).scalars().all()
