import asyncio
import json
import logging
from datetime import datetime, timezone

from fastapi import WebSocket, WebSocketDisconnect
from starlette.websockets import WebSocketState

from src.body.body_state import build_body_state
from src.core.config import load_settings
from src.core.directive_manager import get_directives
from src.core.event_manager import get_latest_event_by_type, get_recent_events
from src.core.state_manager import get_or_create_state
from src.safety.safety_guard import check_system_limits
from src.scheduler.tick_scheduler import is_running

logger = logging.getLogger("digiorg.websocket")


def _clean_thought(raw: str | None) -> str | None:
    if raw is None:
        return None
    return raw.replace("Digiorg piensa: ", "").strip()


def _build_payload() -> dict:
    state = get_or_create_state()
    directive_list = get_directives()
    active_directives = [d.name for d in directive_list if d.is_active]
    body = build_body_state(state)
    recent_events = get_recent_events(limit=20)
    latest_autonomous = get_latest_event_by_type("autonomous_action")
    latest_thought = get_latest_event_by_type("brain_thought")
    safety = check_system_limits()

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "state": {
            "name": state.name,
            "energy": state.energy,
            "hunger": state.hunger,
            "sleepiness": state.sleepiness,
            "hygiene": state.hygiene,
            "mood": state.mood,
            "alive": state.alive,
            "last_tick": state.last_tick.isoformat(),
            "active_directives": active_directives,
        },
        "body": body,
        "thought": _clean_thought(
            latest_thought.description if latest_thought else None
        ),
        "latest_action": (
            {
                "description": latest_autonomous.description,
                "created_at": latest_autonomous.created_at.isoformat(),
            }
            if latest_autonomous else None
        ),
        "events": [
            {
                "id": e.id,
                "event_type": e.event_type,
                "description": e.description,
                "created_at": e.created_at.isoformat(),
            }
            for e in recent_events
        ],
        "safety": {
            "safe": safety["safe"],
            "violations": safety["violations"],
        },
        "scheduler_running": is_running(),
    }


async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    settings = load_settings()
    tick_seconds = settings["life"]["tick_seconds"]
    logger.info("Cliente WebSocket conectado.")

    try:
        while True:
            if websocket.client_state != WebSocketState.CONNECTED:
                break

            try:
                payload = _build_payload()
                await websocket.send_text(json.dumps(payload))
            except RuntimeError as e:
                logger.debug(f"WebSocket cerrado durante envío: {e}")
                break
            except Exception as e:
                logger.exception(f"Error construyendo payload WebSocket: {e}")
                break

            await asyncio.sleep(tick_seconds)

    except WebSocketDisconnect:
        logger.info("Cliente WebSocket desconectado.")
    except Exception as e:
        logger.debug(f"WebSocket finalizado: {e}")
    finally:
        logger.info("Conexión WebSocket cerrada.")