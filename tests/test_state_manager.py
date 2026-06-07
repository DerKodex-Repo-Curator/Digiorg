from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

from src.core.models import VitalState


def _make_state(**kwargs) -> VitalState:
    defaults = dict(
        id=1,
        name="Digiorg",
        energy=50,
        hunger=30,
        sleepiness=30,
        hygiene=80,
        mood="stable",
        alive=True,
        last_tick=datetime.now(timezone.utc),
    )
    defaults.update(kwargs)
    return VitalState(**defaults)


def _mock_session(state):
    mock_session = MagicMock()
    mock_session.__enter__ = lambda s, *a: mock_session
    mock_session.__exit__ = MagicMock(return_value=False)
    mock_session.execute.return_value.scalar_one.return_value = state
    return MagicMock(return_value=mock_session)


def test_passive_energy_recovery_when_stable():
    """Cuando hunger < 65 y sleepiness < 65, la energía se recupera."""
    state = _make_state(energy=50, hunger=30, sleepiness=30)
    mock_sf = _mock_session(state)

    with patch("src.core.state_manager.SessionLocal", mock_sf), \
         patch("src.core.state_manager.decide_and_act", return_value=None), \
         patch("src.core.state_manager.log_event"):
        from src.core.state_manager import update_state_tick
        update_state_tick()

    # energy -1 (degradación) +2 (recuperación pasiva) = net +1
    assert state.energy == 51


def test_no_passive_recovery_when_hungry():
    """Cuando hunger >= 65 no hay recuperación pasiva."""
    state = _make_state(energy=50, hunger=70, sleepiness=30)
    mock_sf = _mock_session(state)

    with patch("src.core.state_manager.SessionLocal", mock_sf), \
         patch("src.core.state_manager.decide_and_act", return_value=None), \
         patch("src.core.state_manager.log_event"):
        from src.core.state_manager import update_state_tick
        update_state_tick()

    # energy -1 (degradación) sin recuperación = 49
    assert state.energy == 49


def test_no_passive_recovery_when_sleepy():
    """Cuando sleepiness >= 65 no hay recuperación pasiva."""
    state = _make_state(energy=50, hunger=30, sleepiness=70)
    mock_sf = _mock_session(state)

    with patch("src.core.state_manager.SessionLocal", mock_sf), \
         patch("src.core.state_manager.decide_and_act", return_value=None), \
         patch("src.core.state_manager.log_event"):
        from src.core.state_manager import update_state_tick
        update_state_tick()

    assert state.energy == 49


def test_energy_penalty_when_critical_stats():
    """Cuando hunger >= 80 o sleepiness >= 80, penalización adicional."""
    state = _make_state(energy=50, hunger=85, sleepiness=30)
    mock_sf = _mock_session(state)

    with patch("src.core.state_manager.SessionLocal", mock_sf), \
         patch("src.core.state_manager.decide_and_act", return_value=None), \
         patch("src.core.state_manager.log_event"):
        from src.core.state_manager import update_state_tick
        update_state_tick()

    # energy -1 (degradación) -1 (penalización) = 48
    assert state.energy == 48


def test_mood_critical_when_energy_low():
    state = _make_state(energy=5, hunger=30, sleepiness=30)
    mock_sf = _mock_session(state)

    with patch("src.core.state_manager.SessionLocal", mock_sf), \
         patch("src.core.state_manager.decide_and_act", return_value=None), \
         patch("src.core.state_manager.log_event"):
        from src.core.state_manager import update_state_tick
        update_state_tick()

    assert state.mood == "critical"


def test_death_when_energy_zero_and_hunger_max():
    state = _make_state(energy=1, hunger=99, sleepiness=30)
    mock_sf = _mock_session(state)

    with patch("src.core.state_manager.SessionLocal", mock_sf), \
         patch("src.core.state_manager.decide_and_act", return_value=None), \
         patch("src.core.state_manager.log_event"):
        from src.core.state_manager import update_state_tick
        update_state_tick()

    assert state.alive is False


def test_energy_capped_at_100():
    state = _make_state(energy=99, hunger=10, sleepiness=10)
    mock_sf = _mock_session(state)

    with patch("src.core.state_manager.SessionLocal", mock_sf), \
         patch("src.core.state_manager.decide_and_act", return_value=None), \
         patch("src.core.state_manager.log_event"):
        from src.core.state_manager import update_state_tick
        update_state_tick()

    assert state.energy <= 100