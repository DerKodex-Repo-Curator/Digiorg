from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base


class VitalState(Base):
    __tablename__ = "vital_state"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), default="Digiorg")
    energy: Mapped[int] = mapped_column(Integer, default=100)
    hunger: Mapped[int] = mapped_column(Integer, default=0)
    sleepiness: Mapped[int] = mapped_column(Integer, default=0)
    hygiene: Mapped[int] = mapped_column(Integer, default=100)
    mood: Mapped[str] = mapped_column(String(30), default="stable")
    alive: Mapped[bool] = mapped_column(Boolean, default=True)
    last_tick: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )