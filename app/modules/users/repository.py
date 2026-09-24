from sqlalchemy import Select, func, or_, select

from app.modules.users.models import Role, User
from app.shared.pagination import Page, PageParams, paginate
from app.shared.repository import SqlRepository


class UserRepository(SqlRepository[User]):
    model = User
    not_found_message = "Usuario no encontrado"

    def get_by_email(self, email: str) -> User | None:
        return self.session.scalar(select(User).where(func.lower(User.email) == email.lower()))

    def search(self, params: PageParams, role: Role | None, search: str | None) -> Page[User]:
        return paginate(self.session, self._list_query(role, search), params)

    def list_clients(self) -> list[User]:
        query = select(User).where(User.role == Role.CLIENT).order_by(User.full_name)
        return list(self.session.scalars(query))

    @staticmethod
    def _list_query(role: Role | None, search: str | None) -> Select[tuple[User]]:
        query = select(User).order_by(User.full_name)
        if role:
            query = query.where(User.role == role)
        if search:
            pattern = f"%{search.lower()}%"
            query = query.where(
                or_(func.lower(User.full_name).like(pattern), func.lower(User.email).like(pattern))
            )
        return query
