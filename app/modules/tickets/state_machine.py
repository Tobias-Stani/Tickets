"""Ticket lifecycle rules. Pure functions: no I/O, trivially testable.

OPEN ──admin takes──▶ IN_PROGRESS
  ▲                        │
  │ client replies    admin replies
  │                        ▼
ANSWERED ◀──admin replies── (any non-closed)

Any non-closed ──admin closes──▶ CLOSED (terminal)
"""

from app.core.errors import ValidationError
from app.modules.tickets.models import TicketStatus
from app.modules.users.models import Role


def ensure_accepts_replies(current: TicketStatus) -> None:
    if current == TicketStatus.CLOSED:
        raise ValidationError(
            "Este ticket está cerrado. Para continuar es necesario crear un ticket nuevo."
        )


def ensure_can_change_status(current: TicketStatus, target: TicketStatus) -> None:
    if current == TicketStatus.CLOSED:
        raise ValidationError("Los tickets cerrados no se pueden modificar.")


def status_after_reply(current: TicketStatus, author_role: Role) -> TicketStatus:
    if author_role == Role.ADMIN:
        return TicketStatus.ANSWERED
    if current == TicketStatus.ANSWERED:
        return TicketStatus.OPEN
    return current
