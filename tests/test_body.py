from datetime import datetime, timezone
from unittest.mock import MagicMock

from src.body.body_state import build_body_state
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
    state = VitalState(**defaults)
    return state


def test_body_stable_state():
    state = _make_state()
    result = build_body_state(state)
    assert result["alive"] is True
    assert result["avatar"] == "( •_•)"
    assert result["vitality_score"] > 0
    assert "physical" in result
    assert "description" in result["physical"]


def test_body_dead_state():
    state = _make_state(alive=False, energy=0)
    result = build_body_state(state)
    assert result["alive"] is False
    assert result["avatar"] == "(✝_✝)"
    assert result["vitality_score"] == 0.0


def test_body_critical_mood():
    state = _make_state(mood="critical", energy=5, hunger=95)
    result = build_body_state(state)
    assert result["avatar"] == "(x_x)"


def test_body_reborn_mood():
    state = _make_state(mood="reborn", energy=100, hunger=0)
    result = build_body_state(state)
    assert result["avatar"] == "( ★_★)"


def test_vitality_score_range():
    state = _make_state(energy=100, hunger=0, sleepiness=0, hygiene=100)
    result = build_body_state(state)
    assert 0 <= result["vitality_score"] <= 100


def test_vitality_score_low_when_degraded():
    state = _make_state(energy=10, hunger=90, sleepiness=90, hygiene=10)
    result = build_body_state(state)
    assert result["vitality_score"] < 30


def test_physical_descriptors_present():
    state = _make_state()
    result = build_body_state(state)
    physical = result["physical"]
    assert "posture" in physical
    assert "activity" in physical
    assert "appearance" in physical
    assert "hunger_state" in physical
    assert "description" in physical