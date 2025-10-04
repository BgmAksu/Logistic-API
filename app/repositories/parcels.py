from collections.abc import Sequence
from typing import Protocol

from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import models


class ParcelRepository(Protocol):
    def create(self, db: Session, obj: models.Parcel) -> models.Parcel: ...
    def get(self, db: Session, parcel_id: int) -> models.Parcel | None: ...
    def list(
        self, db: Session, *, shipment_id: int | None, limit: int, offset: int
    ) -> Sequence[models.Parcel]: ...


class SqlAlchemyParcelRepository:
    def create(self, db: Session, obj: models.Parcel) -> models.Parcel:
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj

    def get(self, db: Session, parcel_id: int) -> models.Parcel | None:
        return db.get(models.Parcel, parcel_id)

    def list(self, db: Session, *, shipment_id: int | None, limit: int, offset: int):
        stmt = select(models.Parcel).limit(limit).offset(offset)
        if shipment_id:
            stmt = stmt.where(models.Parcel.shipment_id == shipment_id)
        return db.execute(stmt).scalars().all()
