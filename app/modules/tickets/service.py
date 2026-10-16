from dataclasses import replace
from uuid import uuid4

from sqlalchemy.orm import Session

from app.core.errors import NotFoundError, ValidationError
from app.core.storage import Storage, StoredObject
from app.modules.tickets.access import ensure_client, get_visible_ticket
from app.modules.tickets.images import ImageFile, ValidatedImage, validate_images
from app.modules.tickets.models import Ticket, TicketImage, TicketMessage, TicketStatus
from app.modules.tickets.repository import TicketRepository
from app.modules.tickets.schemas import TicketCreate, TicketFilters
from app.modules.topics.repository import TopicRepository
from app.modules.users.models import User
from app.shared.pagination import Page, PageParams


class TicketService:
    def __init__(self, session: Session, storage: Storage) -> None:
        self._session = session
        self._storage = storage
        self._tickets = TicketRepository(session)
        self._topics = TopicRepository(session)

    def get_for(self, actor: User, ticket_id: int) -> Ticket:
        return get_visible_ticket(self._tickets, actor, ticket_id)

    def open_for(self, actor: User, ticket_id: int) -> Ticket:
        """Viewing a ticket clears the viewer's side unread flag."""
        ticket = self.get_for(actor, ticket_id)
        if actor.is_admin:
            ticket.unread_by_admin = False
        else:
            ticket.unread_by_client = False
        self._session.commit()
        return ticket

    def unread_count(self, actor: User) -> int:
        client_id = None if actor.is_admin else actor.id
        return self._tickets.count(TicketFilters(client_id=client_id, unread_by=actor.role))

    def list_for_client(
        self, client: User, filters: TicketFilters, params: PageParams
    ) -> Page[Ticket]:
        return self._tickets.find_page(replace(filters, client_id=client.id), params)

    def list_all(self, filters: TicketFilters, params: PageParams) -> Page[Ticket]:
        return self._tickets.find_page(filters, params)

    def status_counts(self) -> dict[TicketStatus, int]:
        return self._tickets.count_by_status()

    def get_image(
        self, actor: User, ticket_id: int, image_id: int
    ) -> tuple[TicketImage, StoredObject]:
        """Any attachment of the ticket (its own or a reply's), if the actor can see the ticket."""
        ticket = self.get_for(actor, ticket_id)
        image = next((image for image in ticket.images if image.id == image_id), None)
        if image is None:
            raise NotFoundError("Archivo no encontrado")
        return image, self._storage.get(image.object_key)

    def create(self, client: User, data: TicketCreate, files: list[ImageFile]) -> Ticket:
        ensure_client(client)
        images = validate_images(files)
        if data.topic_id is not None:
            self._ensure_topic_is_active(data.topic_id)
        ticket = self._tickets.add(Ticket(client_id=client.id, **data.model_dump()))
        client.ticket_count = User.ticket_count + 1  # atomic increment in SQL
        commit_with_attachments(self._session, self._storage, ticket, images)
        return ticket

    def _ensure_topic_is_active(self, topic_id: int) -> None:
        if not self._topics.get_or_raise(topic_id).is_active:
            raise ValidationError("Este tema ya no está disponible.")


def commit_with_attachments(
    session: Session,
    storage: Storage,
    ticket: Ticket,
    files: list[ValidatedImage],
    message: TicketMessage | None = None,
) -> None:
    """Uploads first, then commits. On any failure, uploaded files are removed.
    Attachments always belong to the ticket; reply attachments also to `message`."""
    uploaded: list[str] = []
    try:
        for file in files:
            key = f"tickets/{ticket.id}/{uuid4().hex}.{file.extension}"
            storage.put(key, file.content, file.content_type)
            uploaded.append(key)
            attachment = TicketImage(
                object_key=key, content_type=file.content_type, filename=file.filename
            )
            ticket.images.append(attachment)
            if message is not None:
                message.attachments.append(attachment)
        session.commit()
    except Exception:
        session.rollback()
        for key in uploaded:
            storage.delete(key)
        raise
