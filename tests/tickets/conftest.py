from collections.abc import Callable

import pytest

from app.modules.tickets.images import ImageFile
from app.modules.tickets.models import Ticket
from app.modules.tickets.schemas import TicketCreate
from app.modules.tickets.service import TicketService
from app.modules.tickets.workflow import TicketWorkflow


@pytest.fixture
def tickets(session, storage) -> TicketService:
    return TicketService(session, storage)


@pytest.fixture
def workflow(session) -> TicketWorkflow:
    return TicketWorkflow(session)


@pytest.fixture
def topic(make_topic):
    return make_topic()


@pytest.fixture
def open_ticket(tickets, client_user, topic) -> Ticket:
    return tickets.create(
        client_user, TicketCreate(topic_id=topic.id, subject="Help", description="Broken"), []
    )


@pytest.fixture
def create_ticket(tickets, topic) -> Callable[..., Ticket]:
    def factory(client, images: list[ImageFile] | None = None, **fields) -> Ticket:
        data = {"topic_id": topic.id, "subject": "Help", "description": "Broken"} | fields
        return tickets.create(client, TicketCreate(**data), images or [])

    return factory
