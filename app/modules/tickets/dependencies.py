from typing import Annotated

from fastapi import Depends, Form, Query, UploadFile
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError

from app.core.storage import Storage
from app.modules.auth.dependencies import CurrentUser, DbSession
from app.modules.files.storage import get_storage
from app.modules.tickets.images import MAX_IMAGE_BYTES, ImageFile
from app.modules.tickets.models import TicketStatus
from app.modules.tickets.schemas import TicketCreate, TicketFilters
from app.modules.tickets.service import TicketService
from app.modules.tickets.workflow import TicketWorkflow
from app.shared.web import optional_int


def get_ticket_service(db: DbSession, storage: Annotated[Storage, Depends(get_storage)]):
    return TicketService(db, storage)


def get_ticket_workflow(db: DbSession) -> TicketWorkflow:
    return TicketWorkflow(db)


async def read_uploads(files: list[UploadFile]) -> list[ImageFile]:
    """Reads at most one byte over the limit, so oversized files fail fast without
    loading the whole thing into memory."""
    return [
        ImageFile(filename=file.filename or "", content=await file.read(MAX_IMAGE_BYTES + 1))
        for file in files
    ]


def ticket_create_form(
    subject: Annotated[str, Form()],
    description: Annotated[str, Form()],
    topic_id: Annotated[str, Form()] = "",
) -> TicketCreate:
    """Multipart routes can't bind a Pydantic model as Form() next to File() params,
    so the model is built here and its errors re-raised as request validation errors."""
    try:
        return TicketCreate(
            topic_id=optional_int(topic_id), subject=subject, description=description
        )
    except ValidationError as error:
        raise RequestValidationError(error.errors()) from error


def ticket_filters(
    user: CurrentUser,
    status: Annotated[str, Query()] = "",
    client_id: Annotated[str, Query()] = "",
    topic_id: Annotated[str, Query()] = "",
    unread: Annotated[str, Query()] = "",
) -> TicketFilters:
    """List filters from the query string; "" means "all". `unread` is per viewer side."""
    return TicketFilters(
        status=TicketStatus(status) if status in TicketStatus else None,
        client_id=optional_int(client_id),
        topic_id=optional_int(topic_id),
        unread_by=user.role if unread else None,
    )


Tickets = Annotated[TicketService, Depends(get_ticket_service)]
Filters = Annotated[TicketFilters, Depends(ticket_filters)]
Workflow = Annotated[TicketWorkflow, Depends(get_ticket_workflow)]
