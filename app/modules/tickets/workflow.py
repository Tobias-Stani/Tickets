from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.errors import ValidationError
from app.modules.tickets.access import ensure_admin, get_visible_ticket
from app.modules.tickets.models import Ticket, TicketMessage, TicketStatus
from app.modules.tickets.repository import TicketRepository
from app.modules.tickets.state_machine import ensure_accepts_replies, ensure_can_change_status
from app.modules.users.models import User


class TicketWorkflow:
    """Conversation and lifecycle use cases. Future home of domain events
    (TicketReplied, TicketStatusChanged) for email notifications."""

    def __init__(self, session: Session) -> None:
        self._session = session
        self._tickets = TicketRepository(session)

    def reply(self, actor: User, ticket_id: int, body: str) -> TicketMessage:
        ticket = get_visible_ticket(self._tickets, actor, ticket_id)
        ensure_accepts_replies(ticket.status)
        message = TicketMessage(author_id=actor.id, body=self._clean_body(body))
        ticket.messages.append(message)
        if actor.is_admin:
            ticket.unread_by_client = True
        else:
            ticket.unread_by_admin = True
        ticket.updated_at = func.now()  # status doesn't change; activity still counts
        self._session.commit()
        return message

    def change_status(self, actor: User, ticket_id: int, status: TicketStatus) -> Ticket:
        ensure_admin(actor)
        ticket = self._tickets.get_or_raise(ticket_id)
        ensure_can_change_status(ticket.status, status)
        ticket.status = status
        self._session.commit()
        return ticket

    @staticmethod
    def _clean_body(body: str) -> str:
        cleaned = body.strip()
        if not cleaned:
            raise ValidationError("La respuesta no puede estar vacía.")
        return cleaned
