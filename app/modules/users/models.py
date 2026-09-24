from enum import StrEnum
from typing import TYPE_CHECKING

from sqlalchemy import Column, Enum, ForeignKey, String, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.shared.models import Base, TimestampMixin

if TYPE_CHECKING:
    from app.modules.tags.models import Tag


class Role(StrEnum):
    ADMIN = "ADMIN"
    CLIENT = "CLIENT"


user_tags = Table(
    "user_tags",
    Base.metadata,
    Column("user_id", ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)


class User(TimestampMixin, Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    full_name: Mapped[str] = mapped_column(String(150))
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[Role] = mapped_column(Enum(Role, native_enum=False, length=20))
    is_active: Mapped[bool] = mapped_column(default=True)
    ticket_count: Mapped[int] = mapped_column(default=0)

    tags: Mapped[list["Tag"]] = relationship(secondary=user_tags, lazy="selectin")

    @property
    def is_admin(self) -> bool:
        return self.role == Role.ADMIN
