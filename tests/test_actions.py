from datetime import datetime, timezone

import pytest

from src.core.models import VitalState


def _create_state(session, **kwargs) -> VitalState:
    defaults = dict(
        name="Digiorg",
        energy=100,
        hunger=50,
        sleepiness=50,
        hygiene=50,
        mood="stable",
        alive=True,
        last_tick=datetime.now(timezone.utc),
    )
    defaults.update(kwargs)
    state = VitalState(**defaults)
    session.add(state)
    session.commit()
    return state


def test_feed_reduces_hunger(patch_session):
    _create_state(patch_session, hunger=80)
    from src.core.actions import feed_digiorg
    result = feed_digiorg()
    assert result.hunger == 55  # 80 - 25
    assert result.mood == "relieved"


def test_feed_increases_energy(patch_session):
    _create_state(patch_session, energy=60, hunger=80)
    from src.core.actions import feed_digiorg
    result = feed_digiorg()
    assert result.energy == 65  # 60 + 5


def test_feed_caps_energy_at_100(patch_session):
    _create_state(patch_session, energy=98, hunger=50)
    from src.core.actions import feed_digiorg
    result = feed_digiorg()
    assert result.energy == 100


def test_feed_caps_hunger_at_0(patch_session):
    _create_state(patch_session, hunger=10)
    from src.core.actions import feed_digiorg
    result = feed_digiorg()
    assert result.hunger == 0


def test_sleep_reduces_sleepiness(patch_session):
    _create_state(patch_session, sleepiness=80)
    from src.core.actions import put_to_sleep
    result = put_to_sleep()
    assert result.sleepiness == 50  # 80 - 30
    assert result.mood == "rested"


def test_sleep_increases_energy(patch_session):
    _create_state(patch_session, energy=50, sleepiness=80)
    from src.core.actions import put_to_sleep
    result = put_to_sleep()
    assert result.energy == 70  # 50 + 20


def test_clean_increases_hygiene(patch_session):
    _create_state(patch_session, hygiene=30)
    from src.core.actions import clean_digiorg
    result = clean_digiorg()
    assert result.hygiene == 70  # 30 + 40
    assert result.mood == "fresh"


def test_clean_caps_hygiene_at_100(patch_session):
    _create_state(patch_session, hygiene=80)
    from src.core.actions import clean_digiorg
    result = clean_digiorg()
    assert result.hygiene == 100


def test_action_skips_if_dead(patch_session):
    _create_state(patch_session, alive=False, hunger=80)
    from src.core.actions import feed_digiorg
    result = feed_digiorg()
    assert result.hunger == 80  # sin cambio
    assert result.alive is False