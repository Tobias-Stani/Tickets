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
            "Este ticket está cerrado. Para continuar es necesario crear un ticket nuevo."
        )


def ensure_can_change_status(current: TicketStatus, target: TicketStatus) -> None:
    if current == TicketStatus.CLOSED:
        raise ValidationError("Los tickets cerrados no se pueden modificar.")
