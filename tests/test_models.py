from datetime import datetime, timezone

from src.core.models import VitalState
from src.core.events import EventLog
from src.core.directives import Directive


def test_vital_state_defaults(session):
    state = VitalState(
        name="Digiorg",
        energy=100,
        hunger=0,
        sleepiness=0,
        hygiene=100,
        mood="stable",
        alive=True,
        last_tick=datetime.now(timezone.utc),
    )
    session.add(state)
    session.commit()

    result = session.get(VitalState, state.id)
    assert result is not None
    assert result.name == "Digiorg"
    assert result.energy == 100
    assert result.hunger == 0
    assert result.alive is True


def test_event_log_creation(session):
    event = EventLog(
        event_type="test",
        description="Evento de prueba",
    )
    session.add(event)
    session.commit()

    result = session.get(EventLog, event.id)
    assert result is not None
    assert result.event_type == "test"
    assert result.description == "Evento de prueba"
    assert isinstance(result.created_at, datetime)


def test_directive_creation(session):
    directive = Directive(
        name="test_directive",
        description="Directriz de prueba",
        is_active=True,
    )
    session.add(directive)
    session.commit()

    result = session.get(Directive, directive.id)
    assert result is not None
    assert result.name == "test_directive"
    assert result.is_active is True