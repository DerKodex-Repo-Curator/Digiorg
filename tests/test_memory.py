from datetime import datetime, timezone

from src.memory.models import StateSnapshot, PatternSummary


def _create_snapshot(session, **kwargs) -> StateSnapshot:
    defaults = dict(
        energy=80,
        hunger=30,
        sleepiness=30,
        hygiene=80,
        mood="stable",
        alive=True,
        recorded_at=datetime.now(timezone.utc),
    )
    defaults.update(kwargs)
    snapshot = StateSnapshot(**defaults)
    session.add(snapshot)
    session.commit()
    return snapshot


def test_snapshot_creation(session):
    snapshot = _create_snapshot(session)
    result = session.get(StateSnapshot, snapshot.id)
    assert result is not None
    assert result.energy == 80
    assert result.mood == "stable"
    assert result.alive is True


def test_multiple_snapshots(session):
    for i in range(5):
        _create_snapshot(session, energy=100 - i * 10)
    snapshots = session.query(StateSnapshot).all()
    assert len(snapshots) == 5


def test_snapshot_records_all_stats(session):
    snapshot = _create_snapshot(
        session, energy=60, hunger=40, sleepiness=20, hygiene=90
    )
    result = session.get(StateSnapshot, snapshot.id)
    assert result.energy == 60
    assert result.hunger == 40
    assert result.sleepiness == 20
    assert result.hygiene == 90


def test_snapshot_alive_false(session):
    snapshot = _create_snapshot(session, alive=False, energy=0)
    result = session.get(StateSnapshot, snapshot.id)
    assert result.alive is False


def test_pattern_summary_creation(session):
    pattern = PatternSummary(
        stat="energy",
        avg_value=65.0,
        min_value=20.0,
        max_value=100.0,
        trend="falling",
        computed_at=datetime.now(timezone.utc),
    )
    session.add(pattern)
    session.commit()

    result = session.get(PatternSummary, pattern.id)
    assert result is not None
    assert result.stat == "energy"
    assert result.trend == "falling"
    assert result.avg_value == 65.0


def test_pattern_all_trends(session):
    for trend in ["rising", "falling", "stable"]:
        pattern = PatternSummary(
            stat="hunger",
            avg_value=50.0,
            min_value=0.0,
            max_value=100.0,
            trend=trend,
            computed_at=datetime.now(timezone.utc),
        )
        session.add(pattern)
    session.commit()
    patterns = session.query(PatternSummary).all()
    trends = {p.trend for p in patterns}
    assert trends == {"rising", "falling", "stable"}