from typing import Annotated

from fastapi import Depends
from sqlalchemy import delete
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.errors import NotFoundError
from app.core.storage import Storage, StoredObject
from app.modules.files.models import StoredFile


class DatabaseStorage:
    """Stores files in Postgres, inside the caller's transaction:
    a rolled-back ticket never leaves orphan files behind."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def put(self, key: str, data: bytes, content_type: str) -> None:
        self._session.add(StoredFile(key=key, data=data, content_type=content_type, size=len(data)))
        self._session.flush()

    def get(self, key: str) -> StoredObject:
        stored = self._session.get(StoredFile, key)
        if stored is None:
            raise NotFoundError("Archivo no encontrado")
        return StoredObject(stored.data, stored.content_type)

    def delete(self, key: str) -> None:
        self._session.execute(delete(StoredFile).where(StoredFile.key == key))


def get_storage(db: Annotated[Session, Depends(get_db)]) -> Storage:
    return DatabaseStorage(db)
