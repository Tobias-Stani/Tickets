from datetime import UTC, datetime

import pytest

from app.core.errors import NotFoundError, PermissionDeniedError, ValidationError
from app.modules.tickets.models import Ticket, TicketStatus


def test_admin_reply_keeps_status_and_history(workflow, open_ticket, admin):
    workflow.change_status(admin, open_ticket.id, TicketStatus.IN_PROGRESS)
    workflow.reply(admin, open_ticket.id, "We are on it")

    assert open_ticket.status == TicketStatus.IN_PROGRESS
    assert open_ticket.unread_by_client
    assert [(m.author_id, m.body) for m in open_ticket.messages] == [(admin.id, "We are on it")]


def test_client_reply_keeps_status_and_notifies_admin(workflow, open_ticket, admin, client_user):
    workflow.change_status(admin, open_ticket.id, TicketStatus.ANSWERED)
    open_ticket.unread_by_admin = False
    workflow.reply(client_user, open_ticket.id, "Still broken")

    assert open_ticket.status == TicketStatus.ANSWERED
    assert open_ticket.unread_by_admin


def test_any_reply_bumps_ticket_activity(workflow, open_ticket, client_user, session):
    session.execute(Ticket.__table__.update().values(updated_at=datetime(2000, 1, 1, tzinfo=UTC)))
    session.refresh(open_ticket)

    workflow.reply(client_user, open_ticket.id, "Any news?")
    session.refresh(open_ticket)

    assert open_ticket.updated_at.year > 2000


def test_nobody_can_reply_to_closed_ticket(workflow, open_ticket, admin, client_user):
    workflow.change_status(admin, open_ticket.id, TicketStatus.CLOSED)

    for actor in (admin, client_user):
        with pytest.raises(ValidationError):
            workflow.reply(actor, open_ticket.id, "Hello?")


def test_client_cannot_reply_to_other_clients_ticket(workflow, open_ticket, make_user):
    with pytest.raises(NotFoundError):
        workflow.reply(make_user(), open_ticket.id, "Hi")


def test_reply_body_cannot_be_blank(workflow, open_ticket, client_user):
    with pytest.raises(ValidationError):
        workflow.reply(client_user, open_ticket.id, "   ")


def test_admin_changes_status(workflow, open_ticket, admin):
    workflow.change_status(admin, open_ticket.id, TicketStatus.IN_PROGRESS)

    assert open_ticket.status == TicketStatus.IN_PROGRESS


def test_client_cannot_change_status(workflow, open_ticket, client_user):
    with pytest.raises(PermissionDeniedError):
        workflow.change_status(client_user, open_ticket.id, TicketStatus.CLOSED)


def test_closed_ticket_cannot_be_reopened(workflow, open_ticket, admin):
    workflow.change_status(admin, open_ticket.id, TicketStatus.CLOSED)

    with pytest.raises(ValidationError):
        workflow.change_status(admin, open_ticket.id, TicketStatus.OPEN)
