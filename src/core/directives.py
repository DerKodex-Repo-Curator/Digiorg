from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base

DIRECTIVE_TYPES = ("sleep", "hunger", "hygiene", "custom")


class Directive(Base):
    __tablename__ = "directive"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    description: Mapped[str] = mapped_column(Text)
    type: Mapped[str] = mapped_column(String(20), default="custom")
    threshold: Mapped[int] = mapped_column(Integer, default=70)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )