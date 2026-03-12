"""Database engine and session."""

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import get_settings

settings = get_settings()
_db_url = settings.database_url
_connect_args = {}
_engine_kw = {}
if "sqlite" in _db_url:
    _connect_args["check_same_thread"] = False
elif "mysql" in _db_url:
    _engine_kw["pool_pre_ping"] = True
engine = create_engine(_db_url, connect_args=_connect_args, **_engine_kw)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Base for ORM models."""
    pass


def get_db():
    """Dependency: yield a DB session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
