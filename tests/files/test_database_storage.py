import pytest

from app.core.errors import NotFoundError
from app.core.storage import StoredObject
from app.modules.files.storage import DatabaseStorage


@pytest.fixture
def db_storage(session) -> DatabaseStorage:
    return DatabaseStorage(session)


def test_put_then_get_returns_same_content(db_storage, session):
    db_storage.put("tickets/1/a.png", b"image-bytes", "image/png")
    session.commit()

    assert db_storage.get("tickets/1/a.png") == StoredObject(b"image-bytes", "image/png")


def test_get_missing_key_raises(db_storage):
    with pytest.raises(NotFoundError):
        db_storage.get("missing")


def test_delete_removes_object(db_storage, session):
    db_storage.put("k", b"x", "image/png")
    db_storage.delete("k")
    session.commit()

    with pytest.raises(NotFoundError):
        db_storage.get("k")


def test_put_is_part_of_the_callers_transaction(db_storage, session):
    db_storage.put("k", b"x", "image/png")
    session.rollback()

    with pytest.raises(NotFoundError):
        db_storage.get("k")
