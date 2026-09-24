from sqlalchemy.orm import Session

from app.core.errors import NotFoundError
from app.shared.models import Base


class SqlRepository[ModelT: Base]:
    """Common data access. Subclasses set `model` and add their own queries."""

    model: type[ModelT]
    not_found_message = "Recurso no encontrado"

    def __init__(self, session: Session) -> None:
        self.session = session

    def get(self, entity_id: int) -> ModelT | None:
        return self.session.get(self.model, entity_id)

    def get_or_raise(self, entity_id: int) -> ModelT:
        entity = self.get(entity_id)
        if entity is None:
            raise NotFoundError(self.not_found_message)
        return entity

    def add(self, entity: ModelT) -> ModelT:
        self.session.add(entity)
        self.session.flush()
        return entity

    def delete(self, entity: ModelT) -> None:
        self.session.delete(entity)
        self.session.flush()
