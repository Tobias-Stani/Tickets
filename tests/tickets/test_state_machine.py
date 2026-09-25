import pytest

from app.core.errors import ValidationError
from app.modules.tickets.models import TicketStatus
from app.modules.tickets.state_machine import ensure_accepts_replies, ensure_can_change_status

OPEN, IN_PROGRESS, ANSWERED, CLOSED = TicketStatus


@pytest.mark.parametrize("current", [OPEN, IN_PROGRESS, ANSWERED])
def test_non_closed_tickets_accept_replies(current):
    ensure_accepts_replies(current)


def test_closed_ticket_rejects_replies():
    with pytest.raises(ValidationError):
        ensure_accepts_replies(CLOSED)


@pytest.mark.parametrize("target", list(TicketStatus))
def test_closed_ticket_cannot_change_status(target):
    with pytest.raises(ValidationError):
        ensure_can_change_status(CLOSED, target)


@pytest.mark.parametrize("current", [OPEN, IN_PROGRESS, ANSWERED])
@pytest.mark.parametrize("target", list(TicketStatus))
def test_open_tickets_can_move_to_any_status(current, target):
    ensure_can_change_status(current, target)
