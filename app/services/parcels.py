from dataclasses import dataclass

from sqlalchemy.orm import Session

from .. import models
from ..repositories.parcels import ParcelRepository, SqlAlchemyParcelRepository
from ..schemas import ParcelIn


@dataclass
class ParcelsService:
    repo: ParcelRepository = SqlAlchemyParcelRepository()

    def create(self, db: Session, payload: ParcelIn) -> models.Parcel:
        # Domain guard: shipment must exist
        if not db.get(models.Shipment, payload.shipment_id):
            raise ValueError("shipment_id does not exist")
        obj = models.Parcel(**payload.model_dump())
        return self.repo.create(db, obj)

    def get(self, db: Session, parcel_id: int) -> models.Parcel | None:
        return self.repo.get(db, parcel_id)

    def list(self, db: Session, *, shipment_id: int | None, limit: int, offset: int):
        return self.repo.list(db, shipment_id=shipment_id, limit=limit, offset=offset)
