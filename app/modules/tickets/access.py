from app.core.errors import NotFoundError, PermissionDeniedError
from app.modules.tickets.models import Ticket
from app.modules.tickets.repository import TicketRepository
from app.modules.users.models import User


def get_visible_ticket(tickets: TicketRepository, actor: User, ticket_id: int) -> Ticket:
    """Admins see every ticket; clients only their own.

    Foreign tickets raise NotFound (not Forbidden) so clients cannot probe which IDs exist.
    """
    ticket = tickets.get_or_raise(ticket_id)
    if not actor.is_admin and ticket.client_id != actor.id:
        raise NotFoundError(tickets.not_found_message)
    return ticket


def ensure_admin(actor: User) -> None:
    if not actor.is_admin:
        raise PermissionDeniedError("Solo los administradores pueden realizar esta acción.")


def ensure_client(actor: User) -> None:
    if actor.is_admin:
        raise PermissionDeniedError("Solo los clientes pueden crear tickets.")
