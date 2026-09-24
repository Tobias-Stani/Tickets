from sqlalchemy.orm import Session

from app.core.errors import ConflictError, ValidationError
from app.core.security import hash_password
from app.modules.tags.repository import TagRepository
from app.modules.users.models import Role, User
from app.modules.users.repository import UserRepository
from app.modules.users.schemas import UserCreate, UserUpdate
from app.shared.pagination import Page, PageParams


class UserService:
    def __init__(self, session: Session) -> None:
        self._session = session
        self._users = UserRepository(session)
        self._tags = TagRepository(session)

    def get(self, user_id: int) -> User:
        return self._users.get_or_raise(user_id)

    def search(
        self, params: PageParams, role: Role | None = None, search: str | None = None
    ) -> Page[User]:
        return self._users.search(params, role, search)

    def list_clients(self) -> list[User]:
        return self._users.list_clients()

    def create(self, data: UserCreate) -> User:
        self._ensure_email_available(data.email)
        user = User(
            email=data.email,
            full_name=data.full_name,
            password_hash=hash_password(data.password),
            role=data.role,
            tags=self._tags.get_many_or_raise(data.tag_ids),
        )
        self._users.add(user)
        self._session.commit()
        return user

    def update(self, user_id: int, data: UserUpdate) -> User:
        user = self.get(user_id)
        self._ensure_email_available(data.email, excluding=user)
        user.email, user.full_name, user.role = data.email, data.full_name, data.role
        user.tags = self._tags.get_many_or_raise(data.tag_ids)
        self._session.commit()
        return user

    def set_password(self, user_id: int, password: str) -> User:
        user = self.get(user_id)
        user.password_hash = hash_password(password)
        self._session.commit()
        return user

    def set_active(self, actor: User, user_id: int, is_active: bool) -> User:
        if actor.id == user_id and not is_active:
            raise ValidationError("No es posible desactivar tu propia cuenta.")
        user = self.get(user_id)
        user.is_active = is_active
        self._session.commit()
        return user

    def set_tags(self, user_id: int, tag_ids: list[int]) -> User:
        user = self.get(user_id)
        user.tags = self._tags.get_many_or_raise(tag_ids)
        self._session.commit()
        return user

    def _ensure_email_available(self, email: str, excluding: User | None = None) -> None:
        existing = self._users.get_by_email(email)
        if existing and existing is not excluding:
            raise ConflictError("Ya existe un usuario con ese email.")
