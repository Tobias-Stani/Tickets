from sqlalchemy.orm import Session

from app.core.errors import ConflictError
from app.modules.tags.models import Tag
from app.modules.tags.repository import TagRepository
from app.modules.tags.schemas import TagInput


class TagService:
    def __init__(self, session: Session) -> None:
        self._session = session
        self._tags = TagRepository(session)

    def list_all(self) -> list[Tag]:
        return self._tags.list_all()

    def get(self, tag_id: int) -> Tag:
        return self._tags.get_or_raise(tag_id)

    def create(self, data: TagInput) -> Tag:
        self._ensure_name_available(data.name)
        tag = self._tags.add(Tag(name=data.name, color=data.color))
        self._session.commit()
        return tag

    def update(self, tag_id: int, data: TagInput) -> Tag:
        tag = self.get(tag_id)
        self._ensure_name_available(data.name, excluding=tag)
        tag.name, tag.color = data.name, data.color
        self._session.commit()
        return tag

    def delete(self, tag_id: int) -> None:
        self._tags.delete(self.get(tag_id))
        self._session.commit()

    def _ensure_name_available(self, name: str, excluding: Tag | None = None) -> None:
        existing = self._tags.get_by_name(name)
        if existing and existing is not excluding:
            raise ConflictError("Ya existe una etiqueta con ese nombre.")
