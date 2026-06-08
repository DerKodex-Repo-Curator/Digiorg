import json
import logging

from sqlalchemy import select, desc

from src.brain.llm_client import query_llm
from src.brain.prompt_builder import build_decision_prompt
from src.core.actions import clean_digiorg, feed_digiorg, put_to_sleep
from src.core.config import load_settings
from src.core.database import SessionLocal
from src.core.directive_manager import get_directives
from src.core.event_manager import log_event
from src.core.models import VitalState

logger = logging.getLogger("digiorg.brain.decision")

_llm_tick_counter = 0
MAX_THOUGHTS_MEMORY = 5


def _get_active_directives():
    return [d for d in get_directives() if d.is_active]


def _get_recent_thoughts() -> list[str]:
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


def parse_llm_response(response: str) -> tuple[str | None, str | None]:
    """Parse the LLM JSON response and return (action, thought)."""
    try:
        start = response.find("{")
        end = response.rfind("}") + 1
        if start == -1 or end == 0:
            return None, None

        data = json.loads(response[start:end])
        action = data.get("action", "none").strip().lower()
        thought = data.get("thought", "").strip()

        if action not in ("feed", "sleep", "clean", "none"):
            logger.warning(f"LLM returned unknown action: {action}. Ignoring.")
            return None, thought

        return action if action != "none" else None, thought

    except json.JSONDecodeError as e:
        logger.warning(f"LLM response not parseable: {e}. Response: {response[:200]}")
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


def _deterministic_directives(state: VitalState, active_directives: list) -> str | None:
    """
    Acts on typed directives (sleep, hunger, hygiene) using their threshold.
    Custom directives are handled exclusively by the LLM.
    """
    for directive in active_directives:
        if directive.type == "sleep" and state.sleepiness >= directive.threshold:
            return "sleep"
        if directive.type == "hunger" and state.hunger >= directive.threshold:
            return "feed"
        if directive.type == "hygiene" and state.hygiene <= directive.threshold:
            return "clean"
    return None


def decide_and_act() -> dict | None:
    global _llm_tick_counter
    settings = load_settings()

    if not settings["autonomy"]["enabled"]:
        return None

    active_directives = _get_active_directives()

    with SessionLocal() as session:
        state = session.execute(select(VitalState)).scalar_one_or_none()

        if state is None or not state.alive:
            return None

        # Deterministic survival — always first
        survival_action = _deterministic_survival(state)
        if survival_action is not None:
            _execute_action(survival_action)
            log_event(
                "autonomous_action",
                f"Digiorg decided to {survival_action} by survival instinct.",
            )
            return {"action": survival_action, "source": "instinct", "thought": None}

        # LLM — only every N ticks
        _llm_tick_counter += 1
        llm_every_n = settings["brain"].get("llm_every_n_ticks", 3)
        llm_enabled = settings["brain"]["llm_enabled"]
        thought = None
        action = None

        if llm_enabled and _llm_tick_counter % llm_every_n == 0:
            recent_thoughts = _get_recent_thoughts()
            prompt = build_decision_prompt(
                state=state,
                active_directives=active_directives,
                settings=settings,
                recent_thoughts=recent_thoughts,
            )
            raw_response = query_llm(prompt)

            if raw_response is not None:
                action, thought = parse_llm_response(raw_response)

                if thought:
                    log_event("brain_thought", thought)
                    logger.debug(f"LLM thought: {thought}")

                if action is not None:
                    _execute_action(action)
                    log_event(
                        "autonomous_action",
                        f"Digiorg decided to {action} by LLM reasoning.",
                    )
                    return {"action": action, "source": "llm", "thought": thought}
            else:
                logger.warning(
                    "Ollama unavailable or no response. "
                    "Using deterministic fallback."
                )

        # Deterministic fallback with typed directives
        action = _deterministic_directives(state, active_directives)

        if action is not None:
            _execute_action(action)
            log_event(
                "autonomous_action",
                f"Digiorg decided to {action} by directive.",
            )
            return {"action": action, "source": "directive", "thought": thought}

    return None