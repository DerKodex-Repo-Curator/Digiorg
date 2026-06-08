from datetime import datetime, timezone
from unittest.mock import patch, MagicMock

from src.core.models import VitalState


def _make_state(**kwargs) -> VitalState:
    defaults = dict(
        id=1,
        name="Digiorg",
        energy=80,
        hunger=30,
        sleepiness=30,
        hygiene=80,
        mood="stable",
        alive=True,
        last_tick=datetime.now(timezone.utc),
    )
    defaults.update(kwargs)
    return VitalState(**defaults)


def _mock_engine(state: VitalState, active_directives: set[str] = None):
    active_directives = active_directives or set()

    mock_session = MagicMock()
    mock_session.__enter__ = lambda s, *a: mock_session
    mock_session.__exit__ = MagicMock(return_value=False)
    mock_session.execute.return_value.scalar_one_or_none.return_value = state

    mock_session_factory = MagicMock(return_value=mock_session)

    mock_directives = []
    for name in active_directives:
        m = MagicMock()
        m.name = name
        m.is_active = True
        mock_directives.append(m)

    return mock_session_factory, mock_directives


def _base_settings(enabled=True):
    return {
        "autonomy": {
            "enabled": enabled,
            "sleep_threshold": 70,
            "hunger_threshold": 70,
            "hygiene_threshold": 40,
        },
        "brain": {
            "llm_enabled": False,
            "llm_every_n_ticks": 999,
        },
    }


def test_no_action_when_autonomy_disabled():
    from src.brain.decision_engine import decide_and_act
    with patch("src.brain.decision_engine.load_settings") as mock_settings:
        mock_settings.return_value = _base_settings(enabled=False)
        result = decide_and_act()
    assert result is None


def test_no_action_when_dead():
    state = _make_state(alive=False)
    mock_sf, _ = _mock_engine(state)

    from src.brain.decision_engine import decide_and_act
    with patch("src.brain.decision_engine.load_settings") as mock_settings, \
         patch("src.brain.decision_engine.SessionLocal", mock_sf), \
         patch("src.brain.decision_engine.get_directives", return_value=[]), \
         patch("src.brain.decision_engine.log_event"):
        mock_settings.return_value = _base_settings()
        result = decide_and_act()
    assert result is None


def test_survival_sleep_on_critical_energy():
    state = _make_state(energy=5, sleepiness=50)
    mock_sf, _ = _mock_engine(state)

    from src.brain.decision_engine import decide_and_act
    with patch("src.brain.decision_engine.load_settings") as mock_settings, \
         patch("src.brain.decision_engine.SessionLocal", mock_sf), \
         patch("src.brain.decision_engine.get_directives", return_value=[]), \
         patch("src.brain.decision_engine.put_to_sleep") as mock_sleep, \
         patch("src.brain.decision_engine.log_event"):
        mock_settings.return_value = _base_settings()
        mock_sleep.return_value = state
        result = decide_and_act()

    assert result is not None
    assert result["action"] == "sleep"
    assert result["source"] == "instinct"
    mock_sleep.assert_called_once()


def test_survival_feed_on_critical_hunger():
    state = _make_state(energy=50, hunger=92)
    mock_sf, _ = _mock_engine(state)

    from src.brain.decision_engine import decide_and_act
    with patch("src.brain.decision_engine.load_settings") as mock_settings, \
         patch("src.brain.decision_engine.SessionLocal", mock_sf), \
         patch("src.brain.decision_engine.get_directives", return_value=[]), \
         patch("src.brain.decision_engine.feed_digiorg") as mock_feed, \
         patch("src.brain.decision_engine.log_event"):
        mock_settings.return_value = _base_settings()
        mock_feed.return_value = state
        result = decide_and_act()

    assert result is not None
    assert result["action"] == "feed"
    assert result["source"] == "instinct"
    mock_feed.assert_called_once()


def test_directive_sleep_threshold():
    state = _make_state(energy=50, sleepiness=75)
    mock_sf, _ = _mock_engine(state)

    mock_directive = MagicMock()
    mock_directive.name = "prioritize_rest"
    mock_directive.is_active = True
    mock_directive.type = "sleep"
    mock_directive.threshold = 70

    from src.brain.decision_engine import decide_and_act
    with patch("src.brain.decision_engine.load_settings") as mock_settings, \
         patch("src.brain.decision_engine.SessionLocal", mock_sf), \
         patch("src.brain.decision_engine.get_directives", return_value=[mock_directive]), \
         patch("src.brain.decision_engine.put_to_sleep") as mock_sleep, \
         patch("src.brain.decision_engine.log_event"):
        mock_settings.return_value = _base_settings()
        mock_sleep.return_value = state
        result = decide_and_act()

    assert result is not None
    assert result["action"] == "sleep"
    assert result["source"] == "directive"


def test_directive_hunger_threshold():
    state = _make_state(energy=50, hunger=75)
    mock_sf, _ = _mock_engine(state)

    mock_directive = MagicMock()
    mock_directive.name = "avoid_critical_hunger"
    mock_directive.is_active = True
    mock_directive.type = "hunger"
    mock_directive.threshold = 70

    from src.brain.decision_engine import decide_and_act
    with patch("src.brain.decision_engine.load_settings") as mock_settings, \
         patch("src.brain.decision_engine.SessionLocal", mock_sf), \
         patch("src.brain.decision_engine.get_directives", return_value=[mock_directive]), \
         patch("src.brain.decision_engine.feed_digiorg") as mock_feed, \
         patch("src.brain.decision_engine.log_event"):
        mock_settings.return_value = _base_settings()
        mock_feed.return_value = state
        result = decide_and_act()

    assert result is not None
    assert result["action"] == "feed"
    assert result["source"] == "directive"


def test_directive_hygiene_threshold():
    state = _make_state(energy=50, hygiene=30)
    mock_sf, _ = _mock_engine(state)

    mock_directive = MagicMock()
    mock_directive.name = "maintain_high_hygiene"
    mock_directive.is_active = True
    mock_directive.type = "hygiene"
    mock_directive.threshold = 40

    from src.brain.decision_engine import decide_and_act
    with patch("src.brain.decision_engine.load_settings") as mock_settings, \
         patch("src.brain.decision_engine.SessionLocal", mock_sf), \
         patch("src.brain.decision_engine.get_directives", return_value=[mock_directive]), \
         patch("src.brain.decision_engine.clean_digiorg") as mock_clean, \
         patch("src.brain.decision_engine.log_event"):
        mock_settings.return_value = _base_settings()
        mock_clean.return_value = state
        result = decide_and_act()

    assert result is not None
    assert result["action"] == "clean"
    assert result["source"] == "directive"


def test_custom_directive_ignored_by_deterministic():
    """Custom directives should not trigger deterministic actions."""
    state = _make_state(energy=50, sleepiness=75)
    mock_sf, _ = _mock_engine(state)

    mock_directive = MagicMock()
    mock_directive.name = "be_more_active"
    mock_directive.is_active = True
    mock_directive.type = "custom"
    mock_directive.threshold = 70

    from src.brain.decision_engine import decide_and_act
    with patch("src.brain.decision_engine.load_settings") as mock_settings, \
         patch("src.brain.decision_engine.SessionLocal", mock_sf), \
         patch("src.brain.decision_engine.get_directives", return_value=[mock_directive]), \
         patch("src.brain.decision_engine.log_event"):
        mock_settings.return_value = _base_settings()
        result = decide_and_act()

    assert result is None


def test_no_action_when_stable():
    state = _make_state(energy=80, hunger=30, sleepiness=30, hygiene=80)
    mock_sf, _ = _mock_engine(state)

    from src.brain.decision_engine import decide_and_act
    with patch("src.brain.decision_engine.load_settings") as mock_settings, \
         patch("src.brain.decision_engine.SessionLocal", mock_sf), \
         patch("src.brain.decision_engine.get_directives", return_value=[]), \
         patch("src.brain.decision_engine.log_event"):
        mock_settings.return_value = _base_settings()
        result = decide_and_act()

    assert result is None