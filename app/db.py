from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from .settings import settings


class Base(DeclarativeBase):
    """Global SQLAlchemy declarative base for ORM models."""

    pass


def get_engine():
    """Create a synchronous SQLAlchemy engine."""
    return create_engine(settings.sqlalchemy_url, pool_pre_ping=True)


# Session factory for request-scoped sessions
# TODO: wire it in routers later
SessionLocal = sessionmaker(bind=get_engine(), autoflush=False, autocommit=False)
