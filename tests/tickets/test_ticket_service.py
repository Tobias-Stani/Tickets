import pytest

from app.core.errors import NotFoundError, PermissionDeniedError, ValidationError
from app.modules.tickets.images import ImageFile
from app.modules.tickets.models import TicketStatus
from app.modules.tickets.schemas import TicketFilters
from app.shared.pagination import PageParams
from tests.tickets.images import JPEG, PNG


def test_create_ticket_starts_open_and_increments_counter(create_ticket, client_user):
    ticket = create_ticket(client_user)
    create_ticket(client_user)

    assert ticket.status == TicketStatus.OPEN
    assert ticket.client_id == client_user.id
    assert client_user.ticket_count == 2


def test_create_ticket_uploads_images(create_ticket, client_user, storage):
    images = [ImageFile("a.png", PNG), ImageFile("b.jpg", JPEG)]

    ticket = create_ticket(client_user, images=images)

    assert len(ticket.images) == 2
    assert {image.object_key for image in ticket.images} == set(storage.objects)
    assert all(key.startswith(f"tickets/{ticket.id}/") for key in storage.objects)


def test_failed_upload_leaves_no_ticket_and_no_orphan_files(
    create_ticket, client_user, storage, session
):
    storage.fail_on_put = True

    with pytest.raises(RuntimeError):
        create_ticket(client_user, images=[ImageFile("a.png", PNG)])

    session.refresh(client_user)
    assert client_user.ticket_count == 0
    assert storage.objects == {}


def test_create_ticket_rejects_inactive_topic(create_ticket, client_user, make_topic):
    retired = make_topic(name="Retired", is_active=False)

    with pytest.raises(ValidationError):
        create_ticket(client_user, topic_id=retired.id)


def test_create_ticket_without_topic(create_ticket, client_user):
    ticket = create_ticket(client_user, topic_id=None)

    assert ticket.topic is None


def test_admin_cannot_create_tickets(create_ticket, admin):
    with pytest.raises(PermissionDeniedError):
        create_ticket(admin)


def test_client_sees_own_ticket(tickets, open_ticket, client_user):
    assert tickets.get_for(client_user, open_ticket.id).id == open_ticket.id


def test_client_cannot_see_other_clients_ticket(tickets, open_ticket, make_user):
    with pytest.raises(NotFoundError):
        tickets.get_for(make_user(), open_ticket.id)


def test_admin_sees_any_ticket(tickets, open_ticket, admin):
    assert tickets.get_for(admin, open_ticket.id).id == open_ticket.id


def test_list_for_client_only_returns_their_tickets(tickets, create_ticket, client_user, make_user):
    create_ticket(client_user)
    create_ticket(make_user())

    page = tickets.list_for_client(client_user, TicketFilters(), PageParams())

    assert page.total == 1


def test_list_for_client_ignores_client_filter_and_filters_status(
    tickets, create_ticket, workflow, admin, client_user, make_user
):
    closed = create_ticket(client_user)
    create_ticket(client_user)
    other = create_ticket(make_user())
    workflow.change_status(admin, closed.id, TicketStatus.CLOSED)

    filters = TicketFilters(client_id=other.client_id, status=TicketStatus.CLOSED)
    page = tickets.list_for_client(client_user, filters, PageParams())

    assert [t.id for t in page.items] == [closed.id]


def test_unread_flags_follow_replies_and_views(
    tickets, workflow, open_ticket, admin, client_user
):
    assert tickets.unread_count(admin) == 1  # new ticket
    assert tickets.unread_count(client_user) == 0

    tickets.open_for(admin, open_ticket.id)
    workflow.reply(admin, open_ticket.id, "On it")
    assert (tickets.unread_count(admin), tickets.unread_count(client_user)) == (0, 1)

    tickets.open_for(client_user, open_ticket.id)
    workflow.reply(client_user, open_ticket.id, "Thanks")
    assert (tickets.unread_count(admin), tickets.unread_count(client_user)) == (1, 0)


def test_client_unread_count_only_counts_their_tickets(
    tickets, workflow, create_ticket, admin, client_user, make_user
):
    other = create_ticket(make_user())
    workflow.reply(admin, other.id, "Hi")

    assert tickets.unread_count(client_user) == 0


def test_admin_list_filters_by_client_and_status(
    tickets, create_ticket, workflow, admin, make_user
):
    alice, bob = make_user(), make_user()
    closed = create_ticket(alice)
    create_ticket(alice)
    create_ticket(bob)
    workflow.change_status(admin, closed.id, TicketStatus.CLOSED)

    by_client = tickets.list_all(TicketFilters(client_id=alice.id), PageParams())
    by_status = tickets.list_all(TicketFilters(status=TicketStatus.OPEN), PageParams())

    assert by_client.total == 2
    assert by_status.total == 2


def test_owner_and_admin_can_read_ticket_image(tickets, create_ticket, client_user, admin):
    ticket = create_ticket(client_user, images=[ImageFile("a.png", PNG)])
    image_id = ticket.images[0].id

    for actor in (client_user, admin):
        stored = tickets.get_image(actor, ticket.id, image_id)
        assert (stored.data, stored.content_type) == (PNG, "image/png")


def test_other_client_cannot_read_ticket_image(tickets, create_ticket, client_user, make_user):
    ticket = create_ticket(client_user, images=[ImageFile("a.png", PNG)])

    with pytest.raises(NotFoundError):
        tickets.get_image(make_user(), ticket.id, ticket.images[0].id)


def test_image_must_belong_to_the_ticket(tickets, create_ticket, client_user):
    with_image = create_ticket(client_user, images=[ImageFile("a.png", PNG)])
    other = create_ticket(client_user)

    with pytest.raises(NotFoundError):
        tickets.get_image(client_user, other.id, with_image.images[0].id)


def test_status_counts_include_every_status(tickets, create_ticket, workflow, admin, client_user):
    first = create_ticket(client_user)
    create_ticket(client_user)
    workflow.change_status(admin, first.id, TicketStatus.IN_PROGRESS)

    counts = tickets.status_counts()

    assert counts == {
        TicketStatus.OPEN: 1,
        TicketStatus.IN_PROGRESS: 1,
        TicketStatus.ANSWERED: 0,
        TicketStatus.CLOSED: 0,
    }
