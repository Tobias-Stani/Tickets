from typing import Annotated

from fastapi import Depends, Form, UploadFile
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError

from app.core.storage import Storage
from app.modules.auth.dependencies import DbSession
from app.modules.files.storage import get_storage
from app.modules.tickets.images import MAX_IMAGE_BYTES, ImageFile
from app.modules.tickets.schemas import TicketCreate
from app.modules.tickets.service import TicketService
from app.modules.tickets.workflow import TicketWorkflow


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
    topic_id: Annotated[int, Form()],
    subject: Annotated[str, Form()],
    description: Annotated[str, Form()],
) -> TicketCreate:
    """Multipart routes can't bind a Pydantic model as Form() next to File() params,
    so the model is built here and its errors re-raised as request validation errors."""
    try:
        return TicketCreate(topic_id=topic_id, subject=subject, description=description)
    except ValidationError as error:
        raise RequestValidationError(error.errors()) from error


Tickets = Annotated[TicketService, Depends(get_ticket_service)]
Workflow = Annotated[TicketWorkflow, Depends(get_ticket_workflow)]
