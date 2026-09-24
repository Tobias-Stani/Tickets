from collections.abc import Iterator
from functools import lru_cache

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

import app.models  # noqa: F401  registers every mapper before the first query
from app.core.config import get_settings


@lru_cache
def get_engine() -> Engine:
    return create_engine(get_settings().database_url, pool_pre_ping=True)


@lru_cache
def get_session_factory() -> sessionmaker[Session]:
    return sessionmaker(bind=get_engine(), expire_on_commit=False)


def get_db() -> Iterator[Session]:
    """Request-scoped session. Services own the commit; anything left is rolled back."""
    session = get_session_factory()()
    try:
        yield session
    finally:
        session.rollback()
        session.close()
