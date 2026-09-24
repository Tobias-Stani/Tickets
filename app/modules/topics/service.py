from sqlalchemy.orm import Session

from app.core.errors import ConflictError
from app.modules.topics.models import Topic
from app.modules.topics.repository import TopicRepository
from app.modules.topics.schemas import TopicInput


class TopicService:
    """Topics are never hard-deleted: deactivating keeps historical tickets intact."""

    def __init__(self, session: Session) -> None:
        self._session = session
        self._topics = TopicRepository(session)

    def list_all(self) -> list[Topic]:
        return self._topics.find_all(only_active=False)

    def list_active(self) -> list[Topic]:
        return self._topics.find_all(only_active=True)

    def get(self, topic_id: int) -> Topic:
        return self._topics.get_or_raise(topic_id)

    def create(self, data: TopicInput) -> Topic:
        self._ensure_name_available(data.name)
        topic = self._topics.add(Topic(name=data.name))
        self._session.commit()
        return topic

    def update(self, topic_id: int, data: TopicInput) -> Topic:
        topic = self.get(topic_id)
        self._ensure_name_available(data.name, excluding=topic)
        topic.name = data.name
        self._session.commit()
        return topic

    def set_active(self, topic_id: int, is_active: bool) -> Topic:
        topic = self.get(topic_id)
        topic.is_active = is_active
        self._session.commit()
        return topic

    def _ensure_name_available(self, name: str, excluding: Topic | None = None) -> None:
        existing = self._topics.get_by_name(name)
        if existing and existing is not excluding:
            raise ConflictError("Ya existe un tema con ese nombre.")
