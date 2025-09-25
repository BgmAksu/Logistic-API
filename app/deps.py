# Provides a request-scoped SQLAlchemy session for FastAPI routers.

from collections.abc import Generator

from .db import SessionLocal


def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
