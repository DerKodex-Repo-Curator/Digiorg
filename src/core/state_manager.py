from datetime import datetime, timezone

from sqlalchemy import select

from src.brain.decision_engine import decide_and_act
from src.core.database import SessionLocal
from src.core.event_manager import log_event
from src.core.models import VitalState


def create_initial_state() -> VitalState:
    return VitalState(
        name="Digiorg",
        energy=100,
        hunger=0,
        sleepiness=0,
        hygiene=100,
        mood="stable",
        alive=True,
        last_tick=datetime.now(timezone.utc),
    )


def get_or_create_state() -> VitalState:
    with SessionLocal() as session:
        state = session.execute(select(VitalState)).scalar_one_or_none()

        if state is None:
            state = create_initial_state()
            session.add(state)
            session.commit()
            session.refresh(state)
            log_event("birth", "Digiorg has been created with initial vital state.")

        return state


def update_state_tick() -> VitalState:
    autonomous_result = decide_and_act()

    with SessionLocal() as session:
        state = session.execute(select(VitalState)).scalar_one()

        if not state.alive:
            return state

        # Natural degradation
        state.hunger     = min(100, state.hunger + 2)
        state.sleepiness = min(100, state.sleepiness + 1)
        state.hygiene    = max(0,   state.hygiene - 1)
        state.energy     = max(0,   state.energy - 1)

        # Passive energy recovery when stats are balanced
        if state.hunger < 65 and state.sleepiness < 65:
            state.energy = min(100, state.energy + 2)

        # Penalty for critical stats
        if state.hunger >= 80 or state.sleepiness >= 80:
            state.energy = max(0, state.energy - 1)

        # Emotional state
        if state.energy <= 10 or state.sleepiness >= 90 or state.hunger >= 90:
            state.mood = "critical"
        elif state.hunger > 80 or state.sleepiness > 80:
            state.mood = "distressed"
        elif state.hunger > 50 or state.sleepiness > 50:
            state.mood = "uncomfortable"
        else:
            state.mood = "stable"

        # Collapse
        if state.energy == 0 and (state.sleepiness >= 100 or state.hunger >= 100):
            state.alive = False
            state.mood = "critical"
            log_event(
                "death",
                "Digiorg has collapsed due to extreme exhaustion or critical hunger with zero energy.",
            )

        state.last_tick = datetime.now(timezone.utc)
        session.commit()
        session.refresh(state)

        description = (
            f"State updated: energy={state.energy}, hunger={state.hunger}, "
            f"sleepiness={state.sleepiness}, hygiene={state.hygiene}, "
            f"mood={state.mood}, alive={state.alive}"
        )

        if autonomous_result is not None:
            description += (
                f", autonomous_action={autonomous_result['action']}"
                f", source={autonomous_result['source']}"
            )

        log_event("tick", description)
        return state