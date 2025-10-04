from collections.abc import Sequence
from typing import Protocol

from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import models


class AddressRepository(Protocol):
    """Abstraction for persistence (Dependency Inversion)."""

    def create(self, db: Session, obj: models.Address) -> models.Address: ...
    def get(self, db: Session, address_id: int) -> models.Address | None: ...
    def list(self, db: Session, *, limit: int, offset: int) -> Sequence[models.Address]: ...


class SqlAlchemyAddressRepository:
    """SQLAlchemy-backed repository."""

    def create(self, db: Session, obj: models.Address) -> models.Address:
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj

    def get(self, db: Session, address_id: int) -> models.Address | None:
        return db.get(models.Address, address_id)

    def list(self, db: Session, *, limit: int, offset: int):
        stmt = select(models.Address).limit(limit).offset(offset)
        return db.execute(stmt).scalars().all()
