from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.shared.models import Base, TimestampMixin


class Topic(TimestampMixin, Base):
    __tablename__ = "topics"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    is_active: Mapped[bool] = mapped_column(default=True)
