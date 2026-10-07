"""Ticket lifecycle rules. Pure functions: no I/O, trivially testable.

Status only changes manually (admin). Replies never change it; they flag the
ticket as unread for the other side instead.

Any non-closed ──admin closes──▶ CLOSED (terminal)
"""

from app.core.errors import ValidationError
from app.modules.tickets.models import TicketStatus


def ensure_accepts_replies(current: TicketStatus) -> None:
    if current == TicketStatus.CLOSED:
        raise ValidationError(
            "Esta consulta está cerrada. Para continuar es necesario crear una consulta nueva."
        )


def ensure_can_change_status(current: TicketStatus, target: TicketStatus) -> None:
    if current == TicketStatus.CLOSED:
        raise ValidationError("Las consultas cerradas no se pueden modificar.")
