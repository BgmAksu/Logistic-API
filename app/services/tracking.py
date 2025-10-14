from dataclasses import dataclass
from datetime import datetime

from sqlalchemy.orm import Session

from .. import models
from ..errors import DomainValidationError
from ..repositories.tracking import SqlAlchemyTrackingRepository, TrackingRepository
from ..schemas import TrackingEventIn


@dataclass
class TrackingService:
    repo: TrackingRepository = SqlAlchemyTrackingRepository()

    def create(self, db: Session, payload: TrackingEventIn) -> models.TrackingEvent:
        # Guard: parcel must exist
        parcel = db.get(models.Parcel, payload.parcel_id)
        if not parcel:
            raise DomainValidationError("parcel_id does not exist")

        evt = models.TrackingEvent(**payload.model_dump())
        evt = self.repo.create(db, evt)

        # Domain rule: mark shipment delivered on DELIVERED
        if payload.code.upper() == "DELIVERED":
            parcel.shipment.status = "DELIVERED"
            parcel.shipment.delivered_at = datetime.utcnow()
            db.commit()
        return evt

    def list_for_parcel(self, db: Session, parcel_id: int):
        return self.repo.list_for_parcel(db, parcel_id)
