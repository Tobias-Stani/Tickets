from dataclasses import dataclass
from typing import Annotated

from pydantic import BaseModel, StringConstraints

from app.modules.tickets.models import TicketStatus

Subject = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=200)]
Body = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=10_000)]


class TicketCreate(BaseModel):
    topic_id: int
    subject: Subject
    description: Body


@dataclass(frozen=True)
class TicketFilters:
    status: TicketStatus | None = None
    client_id: int | None = None
    topic_id: int | None = None
