from uuid import uuid4

from sqlalchemy.orm import Session

from app.core.errors import NotFoundError, ValidationError
from app.core.storage import Storage, StoredObject
from app.modules.tickets.access import ensure_client, get_visible_ticket
from app.modules.tickets.images import ImageFile, ValidatedImage, validate_images
from app.modules.tickets.models import Ticket, TicketImage, TicketStatus
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

    def list_for_client(self, client: User, params: PageParams) -> Page[Ticket]:
        return self._tickets.find_page(TicketFilters(client_id=client.id), params)

    def list_all(self, filters: TicketFilters, params: PageParams) -> Page[Ticket]:
        return self._tickets.find_page(filters, params)

    def status_counts(self) -> dict[TicketStatus, int]:
        return self._tickets.count_by_status()

    def get_image(self, actor: User, ticket_id: int, image_id: int) -> StoredObject:
        ticket = self.get_for(actor, ticket_id)
        image = next((image for image in ticket.images if image.id == image_id), None)
        if image is None:
            raise NotFoundError("Imagen no encontrada")
        return self._storage.get(image.object_key)

    def create(self, client: User, data: TicketCreate, files: list[ImageFile]) -> Ticket:
        ensure_client(client)
        images = validate_images(files)
        self._ensure_topic_is_active(data.topic_id)
        ticket = self._tickets.add(Ticket(client_id=client.id, **data.model_dump()))
        client.ticket_count = User.ticket_count + 1  # atomic increment in SQL
        self._commit_with_images(ticket, images)
        return ticket

    def _ensure_topic_is_active(self, topic_id: int) -> None:
        if not self._topics.get_or_raise(topic_id).is_active:
            raise ValidationError("Este tema ya no está disponible.")

    def _commit_with_images(self, ticket: Ticket, images: list[ValidatedImage]) -> None:
        """Uploads first, then commits. On any failure, uploaded files are removed."""
        uploaded: list[str] = []
        try:
            for image in images:
                uploaded.append(self._upload(ticket, image))
            self._session.commit()
        except Exception:
            self._session.rollback()
            for key in uploaded:
                self._storage.delete(key)
            raise

    def _upload(self, ticket: Ticket, image: ValidatedImage) -> str:
        key = f"tickets/{ticket.id}/{uuid4().hex}.{image.extension}"
        self._storage.put(key, image.content, image.content_type)
        ticket.images.append(TicketImage(object_key=key, content_type=image.content_type))
        return key
