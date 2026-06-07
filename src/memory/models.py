from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base


class StateSnapshot(Base):
    __tablename__ = "state_snapshot"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    energy: Mapped[int] = mapped_column(Integer)
    hunger: Mapped[int] = mapped_column(Integer)
    sleepiness: Mapped[int] = mapped_column(Integer)
    hygiene: Mapped[int] = mapped_column(Integer)
    mood: Mapped[str] = mapped_column(String(30))
    alive: Mapped[bool] = mapped_column(Integer)
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )


class PatternSummary(Base):
    __tablename__ = "pattern_summary"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    stat: Mapped[str] = mapped_column(String(50))
    avg_value: Mapped[float] = mapped_column(Float)
    min_value: Mapped[float] = mapped_column(Float)
    max_value: Mapped[float] = mapped_column(Float)
    trend: Mapped[str] = mapped_column(String(20))
    computed_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )