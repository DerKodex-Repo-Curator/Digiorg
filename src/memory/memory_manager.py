import logging
from datetime import datetime

from sqlalchemy import select, func

from src.core.database import SessionLocal
from src.core.models import VitalState
from src.memory.models import PatternSummary, StateSnapshot

logger = logging.getLogger("digiorg.memory")

TRACKED_STATS = ["energy", "hunger", "sleepiness", "hygiene"]


def save_snapshot() -> StateSnapshot:
    with SessionLocal() as session:
        state = session.execute(select(VitalState)).scalar_one_or_none()

        if state is None:
            raise RuntimeError("No existe estado vital para guardar snapshot.")

        snapshot = StateSnapshot(
            energy=state.energy,
            hunger=state.hunger,
            sleepiness=state.sleepiness,
            hygiene=state.hygiene,
            mood=state.mood,
            alive=state.alive,
            recorded_at=datetime.utcnow(),
        )

        session.add(snapshot)
        session.commit()
        session.refresh(snapshot)

        logger.debug(f"Snapshot guardado — id={snapshot.id} mood={snapshot.mood}")
        return snapshot


def get_snapshots(limit: int = 50) -> list[StateSnapshot]:
    with SessionLocal() as session:
        result = session.execute(
            select(StateSnapshot)
            .order_by(StateSnapshot.recorded_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())


def compute_patterns() -> list[PatternSummary]:
    with SessionLocal() as session:
        snapshots = list(
            session.execute(
                select(StateSnapshot).order_by(StateSnapshot.recorded_at.desc()).limit(100)
            ).scalars().all()
        )

        if len(snapshots) < 2:
            logger.warning("Insuficientes snapshots para calcular patrones.")
            return []

        summaries = []

        for stat in TRACKED_STATS:
            values = [getattr(s, stat) for s in snapshots]
            avg = sum(values) / len(values)
            min_val = min(values)
            max_val = max(values)

            # Tendencia: comparar primera mitad con segunda mitad
            mid = len(values) // 2
            first_half_avg = sum(values[mid:]) / len(values[mid:])
            second_half_avg = sum(values[:mid]) / len(values[:mid])

            if second_half_avg > first_half_avg + 2:
                trend = "rising"
            elif second_half_avg < first_half_avg - 2:
                trend = "falling"
            else:
                trend = "stable"

            summary = PatternSummary(
                stat=stat,
                avg_value=round(avg, 2),
                min_value=float(min_val),
                max_value=float(max_val),
                trend=trend,
                computed_at=datetime.utcnow(),
            )
            session.add(summary)
            summaries.append(summary)

        session.commit()
        for s in summaries:
            session.refresh(s)

        logger.info(f"Patrones calculados para {len(summaries)} stats.")
        return summaries


def get_latest_patterns() -> list[PatternSummary]:
    with SessionLocal() as session:
        subquery = (
            select(
                PatternSummary.stat,
                func.max(PatternSummary.computed_at).label("latest")
            )
            .group_by(PatternSummary.stat)
            .subquery()
        )

        result = session.execute(
            select(PatternSummary).join(
                subquery,
                (PatternSummary.stat == subquery.c.stat)
                & (PatternSummary.computed_at == subquery.c.latest),
            )
        )
        return list(result.scalars().all())