from datetime import datetime

from sqlalchemy import DateTime, LargeBinary, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.shared.models import Base


class StoredFile(Base):
    __tablename__ = "stored_files"

    key: Mapped[str] = mapped_column(String(255), primary_key=True)
    content_type: Mapped[str] = mapped_column(String(50))
    size: Mapped[int]
    data: Mapped[bytes] = mapped_column(LargeBinary)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
