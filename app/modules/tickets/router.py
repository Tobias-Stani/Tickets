"""Ticket routes shared by both roles (detail, replies, images) and client-only routes."""

from typing import Annotated
from urllib.parse import quote

from fastapi import APIRouter, Depends, File, Form, Request, UploadFile
from fastapi.responses import Response

from app.core.templates import templates
from app.modules.auth.dependencies import ClientUser, CurrentUser, DbSession
from app.modules.tickets.dependencies import (
    Filters,
    Tickets,
    Workflow,
    read_uploads,
    ticket_create_form,
)
from app.modules.tickets.images import ACCEPT, MAX_IMAGES
from app.modules.tickets.schemas import TicketCreate
from app.modules.topics.service import TopicService
from app.shared.web import Pagination, redirect

router = APIRouter(prefix="/tickets", tags=["tickets"])


@router.get("")
def my_tickets(
    request: Request,
    client: ClientUser,
    tickets: Tickets,
    db: DbSession,
    params: Pagination,
    filters: Filters,
):
    context = {
        "page": tickets.list_for_client(client, filters, params),
        "filters": filters,
        "topic_options": [(t.id, t.name) for t in TopicService(db).list_all()],
    }
    return templates.TemplateResponse(request, "tickets/client_list.html", context)


@router.get("/notifications")
def notifications(request: Request, user: CurrentUser, tickets: Tickets):
    """Polled by the header bell."""
    context = {"unread": tickets.unread_count(user)}
    return templates.TemplateResponse(request, "tickets/_notifications.html", context)


@router.get("/new")
def new_ticket_form(request: Request, _: ClientUser, db: DbSession):
    topic_options = [(topic.id, topic.name) for topic in TopicService(db).list_active()]
    context = {"topic_options": topic_options, "max_images": MAX_IMAGES, "accept": ACCEPT}
    return templates.TemplateResponse(request, "tickets/new.html", context)


@router.post("")
async def create_ticket(
    request: Request,
    client: ClientUser,
    tickets: Tickets,
    data: Annotated[TicketCreate, Depends(ticket_create_form)],
    images: Annotated[list[UploadFile], File()] = [],  # noqa: B006  FastAPI form default
):
    ticket = tickets.create(client, data, await read_uploads(images))
    return redirect(request, f"/tickets/{ticket.id}", "Consulta creada. Te responderemos pronto.")


@router.get("/{ticket_id}")
def ticket_detail(request: Request, user: CurrentUser, tickets: Tickets, ticket_id: int):
    context = {
        "ticket": tickets.open_for(user, ticket_id),
        "max_images": MAX_IMAGES,
        "accept": ACCEPT,
    }
    return templates.TemplateResponse(request, "tickets/detail.html", context)


@router.post("/{ticket_id}/replies")
async def reply(
    request: Request,
    user: CurrentUser,
    workflow: Workflow,
    ticket_id: int,
    body: Annotated[str, Form()] = "",
    files: Annotated[list[UploadFile], File()] = [],  # noqa: B006  FastAPI form default
):
    workflow.reply(user, ticket_id, body, await read_uploads(files))
    return redirect(request, f"/tickets/{ticket_id}", "Respuesta enviada.")


@router.get("/{ticket_id}/images/{image_id}")
def ticket_image(user: CurrentUser, tickets: Tickets, ticket_id: int, image_id: int):
    """Serves any attachment. Images display inline; documents always download."""
    attachment, stored = tickets.get_image(user, ticket_id, image_id)
    headers = {"Cache-Control": "private, max-age=3600", "X-Content-Type-Options": "nosniff"}
    if not attachment.is_image:
        name = quote(attachment.filename or f"archivo-{attachment.id}")
        headers["Content-Disposition"] = f"attachment; filename*=UTF-8''{name}"
    return Response(stored.data, media_type=stored.content_type, headers=headers)
