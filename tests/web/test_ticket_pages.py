import pytest

from app.models import Ticket
from app.modules.tickets.models import TicketStatus
from tests.tickets.images import PNG
from tests.web.conftest import login


@pytest.fixture
def ticket_id(web, htmx_post, client_user, make_topic, session) -> int:
    topic = make_topic()
    login(web, client_user.email)
    data = {"topic_id": str(topic.id), "subject": "No funciona", "description": "Detalle"}
    files = [("images", ("captura.png", PNG, "image/png"))]

    response = htmx_post("/tickets", data=data, files=files)

    ticket = session.query(Ticket).one()
    assert response.headers["HX-Redirect"] == f"/tickets/{ticket.id}"
    return ticket.id


def test_client_pages_render(web, client_user, make_topic):
    make_topic()
    login(web, client_user.email)

    assert web.get("/tickets").status_code == 200
    assert "Sin tema" in web.get("/tickets/new").text


def test_client_can_create_ticket_without_topics(web, htmx_post, client_user, session):
    login(web, client_user.email)
    assert 'name="subject"' in web.get("/tickets/new").text

    htmx_post("/tickets", data={"subject": "Hola", "description": "Detalle"})

    ticket = session.query(Ticket).one()
    assert ticket.topic_id is None
    assert "Sin tema" in web.get(f"/tickets/{ticket.id}").text


def test_created_ticket_shows_detail_and_image(web, ticket_id, session):
    page = web.get(f"/tickets/{ticket_id}")
    image_id = session.get(Ticket, ticket_id).images[0].id

    assert "No funciona" in page.text
    assert "Ticket creado" in page.text
    image = web.get(f"/tickets/{ticket_id}/images/{image_id}")
    assert (image.content, image.headers["content-type"]) == (PNG, "image/png")


def test_other_client_cannot_see_ticket(web, ticket_id, make_user):
    other = make_user()
    web.cookies.clear()
    login(web, other.email)

    assert web.get(f"/tickets/{ticket_id}").status_code == 404


def test_admin_reply_and_close_flow(web, htmx_post, ticket_id, admin, client_user, session):
    web.cookies.clear()
    login(web, admin.email)
    htmx_post(f"/tickets/{ticket_id}/replies", data={"body": "Ya lo revisamos"})
    htmx_post(f"/admin/tickets/{ticket_id}/status", data={"status": "CLOSED"})

    ticket = session.get(Ticket, ticket_id)
    session.refresh(ticket)
    assert ticket.status == TicketStatus.CLOSED
    assert "Ya lo revisamos" in web.get(f"/tickets/{ticket_id}").text

    web.cookies.clear()
    login(web, client_user.email)
    response = htmx_post(f"/tickets/{ticket_id}/replies", data={"body": "Hola?"})
    assert response.status_code == 422
    assert "está cerrado" in response.text


def test_admin_filters_tickets_by_status(web, ticket_id, admin):
    web.cookies.clear()
    login(web, admin.email)

    assert "No funciona" in web.get("/admin/tickets?status=OPEN").text
    assert "No funciona" not in web.get("/admin/tickets?status=CLOSED").text


def test_client_filters_tickets_by_status(web, ticket_id):
    assert "No funciona" in web.get("/tickets?status=OPEN").text
    assert "No funciona" not in web.get("/tickets?status=CLOSED").text


def test_bell_shows_unread_count_until_ticket_is_viewed(
    web, htmx_post, ticket_id, admin, session
):
    web.cookies.clear()
    login(web, admin.email)
    assert "1 ticket(s) con novedades" in web.get("/tickets/notifications").text
    assert "No funciona" in web.get("/admin/tickets?unread=1").text

    web.get(f"/tickets/{ticket_id}")

    assert "Sin novedades" in web.get("/tickets/notifications").text
    assert "No funciona" not in web.get("/admin/tickets?unread=1").text

    htmx_post(f"/tickets/{ticket_id}/replies", data={"body": "Ya lo revisamos"})
    session.refresh(ticket := session.get(Ticket, ticket_id))
    assert ticket.status == TicketStatus.OPEN
