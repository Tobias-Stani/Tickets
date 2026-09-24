from sqlalchemy import Select, func, select

from app.modules.tickets.models import Ticket, TicketStatus
from app.modules.tickets.schemas import TicketFilters
from app.shared.pagination import Page, PageParams, paginate
from app.shared.repository import SqlRepository


class TicketRepository(SqlRepository[Ticket]):
    model = Ticket
    not_found_message = "Ticket no encontrado"

    def find_page(self, filters: TicketFilters, params: PageParams) -> Page[Ticket]:
        return paginate(self.session, self._filtered_query(filters), params)

    def count_by_status(self) -> dict[TicketStatus, int]:
        rows = self.session.execute(select(Ticket.status, func.count()).group_by(Ticket.status))
        counts = dict(rows.tuples().all())
        return {status: counts.get(status, 0) for status in TicketStatus}

    @staticmethod
    def _filtered_query(filters: TicketFilters) -> Select[tuple[Ticket]]:
        query = select(Ticket).order_by(Ticket.updated_at.desc(), Ticket.id.desc())
        if filters.status:
            query = query.where(Ticket.status == filters.status)
        if filters.client_id:
            query = query.where(Ticket.client_id == filters.client_id)
        if filters.topic_id:
            query = query.where(Ticket.topic_id == filters.topic_id)
        return query
