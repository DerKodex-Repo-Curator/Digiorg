import json
import logging

from sqlalchemy import select, desc

from src.brain.llm_client import query_llm
from src.brain.prompt_builder import build_decision_prompt
from src.core.actions import clean_digiorg, feed_digiorg, put_to_sleep
from src.core.config import load_settings
from src.core.database import SessionLocal
from src.core.directive_manager import get_directives
from src.core.event_manager import get_recent_events, log_event
from src.core.models import VitalState

logger = logging.getLogger("digiorg.brain.decision")

_llm_tick_counter = 0
MAX_THOUGHTS_MEMORY = 5


def _get_active_directive_names() -> set[str]:
    directives = get_directives()
    return {directive.name for directive in directives if directive.is_active}


def _get_recent_thoughts() -> list[str]:
    """Recupera los últimos pensamientos desde la base de datos."""
    from src.core.events import EventLog
    with SessionLocal() as session:
        result = session.execute(
            select(EventLog)
            .where(EventLog.event_type == "brain_thought")
            .order_by(desc(EventLog.created_at))
            .limit(MAX_THOUGHTS_MEMORY)
        )
        events = list(result.scalars().all())
        return [e.description for e in reversed(events)]


def _parse_llm_response(response: str) -> tuple[str | None, str | None]:
    try:
        start = response.find("{")
        end = response.rfind("}") + 1
        if start == -1 or end == 0:
            return None, None

        data = json.loads(response[start:end])
        action = data.get("action", "none").strip().lower()
        thought = data.get("thought", "").strip()

        if action not in ("feed", "sleep", "clean", "none"):
            logger.warning(f"LLM devolvió acción desconocida: {action}. Ignorando.")
            return None, thought

        return action if action != "none" else None, thought

    except json.JSONDecodeError as e:
        logger.warning(f"LLM respuesta no parseable: {e}. Respuesta: {response[:200]}")
        return None, None


def _execute_action(action: str) -> None:
    if action == "feed":
        feed_digiorg()
    elif action == "sleep":
        put_to_sleep()
    elif action == "clean":
        clean_digiorg()


def _deterministic_survival(state: VitalState) -> str | None:
    if state.energy <= 10 or state.sleepiness >= 95:
        return "sleep"
    if state.hunger >= 90:
        return "feed"
    return None


def _deterministic_directives(
    state: VitalState,
    active_directives: set[str],
    autonomy: dict,
) -> str | None:
    if (
        "priorizar_descanso" in active_directives
        and state.sleepiness >= autonomy["sleep_threshold"]
    ):
        return "sleep"
    if (
        "evitar_hambre_critica" in active_directives
        and state.hunger >= autonomy["hunger_threshold"]
    ):
        return "feed"
    if (
        "mantener_higiene_alta" in active_directives
        and state.hygiene <= autonomy["hygiene_threshold"]
    ):
        return "clean"
    return None


def decide_and_act() -> dict | None:
    global _llm_tick_counter
    settings = load_settings()

    if not settings["autonomy"]["enabled"]:
        return None

    active_directives = _get_active_directive_names()

    with SessionLocal() as session:
        state = session.execute(select(VitalState)).scalar_one_or_none()

        if state is None or not state.alive:
            return None

        # Supervivencia determinista — siempre primero
        survival_action = _deterministic_survival(state)
        if survival_action is not None:
            _execute_action(survival_action)
            log_event(
                "autonomous_action",
                f"Digiorg ha decidido {survival_action} por instinto de supervivencia.",
            )
            return {"action": survival_action, "source": "instinct", "thought": None}

        # LLM — solo cada N ticks
        _llm_tick_counter += 1
        llm_every_n = settings["brain"].get("llm_every_n_ticks", 3)
        llm_enabled = settings["brain"]["llm_enabled"]
        thought = None
        action = None

        if llm_enabled and _llm_tick_counter % llm_every_n == 0:
            recent_thoughts = _get_recent_thoughts()
            prompt = build_decision_prompt(
                state=state,
                active_directives=list(active_directives),
                settings=settings,
                recent_thoughts=recent_thoughts,
            )
            raw_response = query_llm(prompt)

            if raw_response is not None:
                action, thought = _parse_llm_response(raw_response)

                if thought:
                    log_event("brain_thought", thought)
                    logger.debug(f"LLM thought: {thought}")

                if action is not None:
                    _execute_action(action)
                    log_event(
                        "autonomous_action",
                        f"Digiorg ha decidido {action} por razonamiento LLM.",
                    )
                    return {"action": action, "source": "llm", "thought": thought}
            else:
                logger.warning(
                    "Ollama no disponible o sin respuesta. "
                    "Usando lógica determinista como fallback."
                )

        # Fallback determinista con directivas
        action = _deterministic_directives(state, active_directives, settings["autonomy"])

        if action is not None:
            _execute_action(action)
            log_event(
                "autonomous_action",
                f"Digiorg ha decidido {action} por directriz.",
            )
            return {"action": action, "source": "directive", "thought": thought}

    return None