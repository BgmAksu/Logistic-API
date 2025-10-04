from collections.abc import Sequence
from typing import Protocol

from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import models


class TrackingRepository(Protocol):
    def create(self, db: Session, obj: models.TrackingEvent) -> models.TrackingEvent: ...
    def list_for_parcel(self, db: Session, parcel_id: int) -> Sequence[models.TrackingEvent]: ...


class SqlAlchemyTrackingRepository:
    def create(self, db: Session, obj: models.TrackingEvent) -> models.TrackingEvent:
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj

    def list_for_parcel(self, db: Session, parcel_id: int):
        stmt = select(models.TrackingEvent).where(models.TrackingEvent.parcel_id == parcel_id)
        return db.execute(stmt).scalars().all()
