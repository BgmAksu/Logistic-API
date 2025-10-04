from dataclasses import dataclass

from sqlalchemy import text
from sqlalchemy.orm import Session

from .. import models
from ..repositories.addresses import AddressRepository, SqlAlchemyAddressRepository
from ..schemas import AddressIn


@dataclass
class AddressesService:
    repo: AddressRepository = SqlAlchemyAddressRepository()

    def create(self, db: Session, payload: AddressIn) -> models.Address:
        obj = models.Address(**payload.model_dump())
        obj = self.repo.create(db, obj)
        # Auto-populate geom if lat/lon provided
        if obj.lat is not None and obj.lon is not None:
            db.execute(
                text(
                    """
                    UPDATE addresses
                    SET geom = ST_SetSRID(ST_MakePoint(:lon, :lat), 4326)
                    WHERE id = :id
                """.strip()
                ),
                {"lon": obj.lon, "lat": obj.lat, "id": obj.id},
            )
            db.commit()
        return obj

    def get(self, db: Session, address_id: int) -> models.Address | None:
        return self.repo.get(db, address_id)

    def list(self, db: Session, *, limit: int, offset: int):
        return self.repo.list(db, limit=limit, offset=offset)
