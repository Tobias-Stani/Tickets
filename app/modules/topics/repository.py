from sqlalchemy import func, select

from app.modules.topics.models import Topic
from app.shared.repository import SqlRepository


class TopicRepository(SqlRepository[Topic]):
    model = Topic
    not_found_message = "Tema no encontrado"

    def get_by_name(self, name: str) -> Topic | None:
        return self.session.scalar(select(Topic).where(func.lower(Topic.name) == name.lower()))

    def find_all(self, only_active: bool) -> list[Topic]:
        query = select(Topic).order_by(Topic.name)
        if only_active:
            query = query.where(Topic.is_active.is_(True))
        return list(self.session.scalars(query))
