from collections.abc import Generator

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import get_settings


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""


_engine: Engine | None = None
_engine_url: str | None = None


def get_engine() -> Engine:
    """Create the SQLAlchemy engine lazily so tests can override settings."""

    global _engine, _engine_url
    settings = get_settings()
    if _engine is None or _engine_url != settings.database_url:
        _engine = create_engine(settings.database_url, pool_pre_ping=True)
        _engine_url = settings.database_url
    return _engine


def get_session_local() -> sessionmaker[Session]:
    return sessionmaker(autocommit=False, autoflush=False, bind=get_engine())


def get_db() -> Generator[Session, None, None]:
    db = get_session_local()()
    try:
        yield db
    finally:
        db.close()
