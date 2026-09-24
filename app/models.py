"""Model registry: importing this module registers every table in `Base.metadata`.

Used by Alembic autogenerate and by anything that needs the full mapper graph.
"""

from app.modules.files.models import StoredFile
from app.modules.tags.models import Tag
from app.modules.tickets.models import Ticket, TicketImage, TicketMessage
from app.modules.topics.models import Topic
from app.modules.users.models import User
from app.shared.models import Base

__all__ = ["Base", "StoredFile", "Tag", "Ticket", "TicketImage", "TicketMessage", "Topic", "User"]
