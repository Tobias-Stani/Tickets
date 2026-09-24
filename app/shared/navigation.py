from dataclasses import dataclass

from app.modules.users.models import User


@dataclass(frozen=True)
class NavItem:
    label: str
    url: str
    icon: str
    exact: bool = False

    def is_active(self, path: str) -> bool:
        return path == self.url if self.exact else path.startswith(self.url)


ADMIN_NAV = (
    NavItem("Inicio", "/admin", "home", exact=True),
    NavItem("Tickets", "/admin/tickets", "ticket"),
    NavItem("Usuarios", "/admin/users", "users"),
    NavItem("Etiquetas", "/admin/tags", "tag"),
    NavItem("Temas", "/admin/topics", "folder"),
)

CLIENT_NAV = (
    NavItem("Mis tickets", "/tickets", "ticket", exact=True),
    NavItem("Nuevo ticket", "/tickets/new", "plus"),
)


def nav_for(user: User | None) -> tuple[NavItem, ...]:
    if user is None:
        return ()
    return ADMIN_NAV if user.is_admin else CLIENT_NAV
