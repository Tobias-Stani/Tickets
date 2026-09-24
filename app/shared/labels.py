"""Spanish display labels for domain values. Templates use these via globals."""

from datetime import UTC, datetime
from zoneinfo import ZoneInfo

from app.core.config import get_settings
from app.modules.tickets.models import TicketStatus
from app.modules.users.models import Role

STATUS_LABELS = {
    TicketStatus.OPEN: "Abierto",
    TicketStatus.IN_PROGRESS: "En proceso",
    TicketStatus.ANSWERED: "Respondido",
    TicketStatus.CLOSED: "Cerrado",
}

ROLE_LABELS = {Role.ADMIN: "Administrador", Role.CLIENT: "Cliente"}


def status_label(status: TicketStatus) -> str:
    return STATUS_LABELS[status]


def status_options() -> list[tuple[str, str]]:
    return [(status.value, label) for status, label in STATUS_LABELS.items()]


def role_options() -> list[tuple[str, str]]:
    return [(role.value, label) for role, label in ROLE_LABELS.items()]


def role_label(role: Role) -> str:
    return ROLE_LABELS[role]


def format_datetime(value: datetime | None) -> str:
    if value is None:
        return ""
    aware = value if value.tzinfo else value.replace(tzinfo=UTC)
    local = aware.astimezone(ZoneInfo(get_settings().timezone))
    return local.strftime("%d/%m/%Y %H:%M")
