from dataclasses import dataclass, field

from app.core.errors import NotFoundError
from app.core.storage import StoredObject


@dataclass
class InMemoryStorage:
    objects: dict[str, StoredObject] = field(default_factory=dict)
    fail_on_put: bool = False

    def put(self, key: str, data: bytes, content_type: str) -> None:
        if self.fail_on_put:
            raise RuntimeError("storage unavailable")
        self.objects[key] = StoredObject(data, content_type)

    def get(self, key: str) -> StoredObject:
        if key not in self.objects:
            raise NotFoundError("Archivo no encontrado")
        return self.objects[key]

    def delete(self, key: str) -> None:
        self.objects.pop(key, None)
