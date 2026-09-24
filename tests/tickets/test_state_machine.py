import pytest

from app.core.errors import ValidationError
from app.modules.tickets.models import TicketStatus
from app.modules.tickets.state_machine import (
    ensure_accepts_replies,
    ensure_can_change_status,
    status_after_reply,
)
from app.modules.users.models import Role

OPEN, IN_PROGRESS, ANSWERED, CLOSED = TicketStatus


@pytest.mark.parametrize("current", [OPEN, IN_PROGRESS, ANSWERED])
def test_admin_reply_marks_ticket_answered(current):
    assert status_after_reply(current, Role.ADMIN) == ANSWERED


def test_client_reply_reopens_answered_ticket():
    assert status_after_reply(ANSWERED, Role.CLIENT) == OPEN


@pytest.mark.parametrize("current", [OPEN, IN_PROGRESS])
def test_client_reply_keeps_status_when_not_answered(current):
    assert status_after_reply(current, Role.CLIENT) == current


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
