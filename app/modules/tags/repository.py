from sqlalchemy import func, select

from app.core.errors import NotFoundError
from app.modules.tags.models import Tag
from app.shared.repository import SqlRepository


class TagRepository(SqlRepository[Tag]):
    model = Tag
    not_found_message = "Etiqueta no encontrada"

    def get_by_name(self, name: str) -> Tag | None:
        return self.session.scalar(select(Tag).where(func.lower(Tag.name) == name.lower()))

    def list_all(self) -> list[Tag]:
        return list(self.session.scalars(select(Tag).order_by(Tag.name)))

    def get_many_or_raise(self, tag_ids: list[int]) -> list[Tag]:
        unique_ids = set(tag_ids)
        tags = list(self.session.scalars(select(Tag).where(Tag.id.in_(unique_ids))))
        if len(tags) != len(unique_ids):
            raise NotFoundError(self.not_found_message)
        return tags
