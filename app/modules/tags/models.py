from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.shared.models import Base, TimestampMixin


class Tag(TimestampMixin, Base):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)
    color: Mapped[str] = mapped_column(String(7), default="#6366f1")
