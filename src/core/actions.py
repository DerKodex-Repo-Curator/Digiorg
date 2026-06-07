from datetime import datetime, timezone

from sqlalchemy import select

from src.core.database import SessionLocal
from src.core.event_manager import log_event
from src.core.models import VitalState


def feed_digiorg() -> VitalState:
    with SessionLocal() as session:
        state = session.execute(select(VitalState)).scalar_one()

        if not state.alive:
            return state

        state.hunger = max(0, state.hunger - 25)
        state.energy = min(100, state.energy + 5)
        state.mood = "relieved"
        state.last_tick = datetime.now(timezone.utc)

        session.commit()
        session.refresh(state)

        log_event("feed", "Digiorg ha comido.")
        return state


def put_to_sleep() -> VitalState:
    with SessionLocal() as session:
        state = session.execute(select(VitalState)).scalar_one()

        if not state.alive:
            return state

        state.sleepiness = max(0, state.sleepiness - 30)
        state.energy = min(100, state.energy + 20)
        state.mood = "rested"
        state.last_tick = datetime.now(timezone.utc)

        session.commit()
        session.refresh(state)

        log_event("sleep", "Digiorg ha dormido.")
        return state


def clean_digiorg() -> VitalState:
    with SessionLocal() as session:
        state = session.execute(select(VitalState)).scalar_one()

        if not state.alive:
            return state

        state.hygiene = min(100, state.hygiene + 40)
        state.mood = "fresh"
        state.last_tick = datetime.now(timezone.utc)

        session.commit()
        session.refresh(state)

        log_event("clean", "Digiorg ha sido limpiado.")
        return state