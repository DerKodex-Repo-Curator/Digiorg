from sqlalchemy import desc, select

from src.core.database import SessionLocal
from src.core.events import EventLog


def log_event(event_type: str, description: str) -> None:
    with SessionLocal() as session:
        event = EventLog(event_type=event_type, description=description)
        session.add(event)
        session.commit()


def get_recent_events(limit: int = 10) -> list[EventLog]:
    with SessionLocal() as session:
        result = session.execute(
            select(EventLog).order_by(desc(EventLog.created_at)).limit(limit)
        )
        return list(result.scalars().all())


def get_latest_event_by_type(event_type: str) -> EventLog | None:
    with SessionLocal() as session:
        result = session.execute(
            select(EventLog)
            .where(EventLog.event_type == event_type)
            .order_by(desc(EventLog.created_at))
            .limit(1)
        )
        return result.scalar_one_or_none()