from datetime import datetime
from enum import StrEnum

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text, false, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.modules.topics.models import Topic
from app.modules.users.models import User
from app.shared.models import Base, TimestampMixin


class TicketStatus(StrEnum):
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    ANSWERED = "ANSWERED"
    CLOSED = "CLOSED"


class Ticket(TimestampMixin, Base):
    __tablename__ = "tickets"

    id: Mapped[int] = mapped_column(primary_key=True)
    client_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    topic_id: Mapped[int | None] = mapped_column(ForeignKey("topics.id"), index=True)
    subject: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(Text)
    status: Mapped[TicketStatus] = mapped_column(
        Enum(TicketStatus, native_enum=False, length=20), default=TicketStatus.OPEN, index=True
    )
    # Each side's "new activity" flag: set by the other side's reply, cleared on viewing.
    unread_by_admin: Mapped[bool] = mapped_column(default=True, server_default=false())
    unread_by_client: Mapped[bool] = mapped_column(default=False, server_default=false())

    client: Mapped[User] = relationship(lazy="joined")
    topic: Mapped[Topic | None] = relationship(lazy="joined")
    images: Mapped[list["TicketImage"]] = relationship(
        back_populates="ticket", cascade="all, delete-orphan", lazy="selectin"
    )
    messages: Mapped[list["TicketMessage"]] = relationship(
        back_populates="ticket",
        cascade="all, delete-orphan",
        order_by="TicketMessage.created_at",
        lazy="selectin",
    )


class TicketImage(Base):
    __tablename__ = "ticket_images"

    id: Mapped[int] = mapped_column(primary_key=True)
    ticket_id: Mapped[int] = mapped_column(ForeignKey("tickets.id", ondelete="CASCADE"))
    object_key: Mapped[str] = mapped_column(String(255), unique=True)
    content_type: Mapped[str] = mapped_column(String(50))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    ticket: Mapped[Ticket] = relationship(back_populates="images")


class TicketMessage(Base):
    __tablename__ = "ticket_messages"

    id: Mapped[int] = mapped_column(primary_key=True)
    ticket_id: Mapped[int] = mapped_column(ForeignKey("tickets.id", ondelete="CASCADE"), index=True)
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    body: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    ticket: Mapped[Ticket] = relationship(back_populates="messages")
    author: Mapped[User] = relationship(lazy="joined")
