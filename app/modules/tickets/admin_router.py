from typing import Annotated

from fastapi import APIRouter, Form, Request

from app.core.templates import templates
from app.modules.auth.dependencies import AdminUser, DbSession
from app.modules.tickets.dependencies import Filters, Tickets, Workflow
from app.modules.tickets.models import TicketStatus
from app.modules.topics.service import TopicService
from app.modules.users.service import UserService
from app.shared.web import Pagination, redirect

router = APIRouter(tags=["admin"])


@router.get("/admin")
def dashboard(request: Request, _: AdminUser, tickets: Tickets):
    context = {"counts": tickets.status_counts()}
    return templates.TemplateResponse(request, "admin/dashboard.html", context)


@router.get("/admin/tickets")
def all_tickets(
    request: Request,
    _: AdminUser,
    tickets: Tickets,
    db: DbSession,
    params: Pagination,
    filters: Filters,
):
    context = {"page": tickets.list_all(filters, params), "filters": filters}
    return templates.TemplateResponse(
        request, "tickets/admin_list.html", context | _filter_options(db)
    )


def _filter_options(db: DbSession) -> dict[str, list[tuple]]:
    return {
        "client_options": [(c.id, c.full_name) for c in UserService(db).list_clients()],
        "topic_options": [(t.id, t.name) for t in TopicService(db).list_all()],
    }


@router.post("/admin/tickets/{ticket_id}/status")
def change_status(
    request: Request,
    admin: AdminUser,
    workflow: Workflow,
    ticket_id: int,
    status: Annotated[TicketStatus, Form()],
):
    workflow.change_status(admin, ticket_id, status)
    return redirect(request, f"/tickets/{ticket_id}", "Estado actualizado.")
