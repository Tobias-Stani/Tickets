from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class StoredObject:
    data: bytes
    content_type: str


class Storage(Protocol):
    """Port for binary file storage.

    Current adapter: `DatabaseStorage` (Postgres). Moving to an object store
    (e.g. a Railway Bucket) only requires a new adapter with this interface.
    """

    def put(self, key: str, data: bytes, content_type: str) -> None: ...

    def get(self, key: str) -> StoredObject: ...

    def delete(self, key: str) -> None: ...
