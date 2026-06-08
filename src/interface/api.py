from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import select

from src.body.body_state import build_body_state
from src.brain.decision_engine import parse_llm_response
from src.brain.llm_client import query_llm
from src.brain.prompt_builder import build_decision_prompt
from src.core.actions import clean_digiorg, feed_digiorg, put_to_sleep
from src.core.bootstrap import init_db
from src.core.config import load_settings
from src.core.database import SessionLocal
from src.core.directive_manager import (
    create_directive,
    delete_directive,
    get_directives,
    set_directive_status,
)
from src.core.directives import DIRECTIVE_TYPES
from src.core.event_manager import get_latest_event_by_type, get_recent_events, log_event
from src.core.logging_config import setup_logging
from src.core.models import VitalState
from src.core.state_manager import get_or_create_state
from src.interface.websocket import websocket_endpoint
from src.memory.memory_manager import compute_patterns, get_latest_patterns, get_snapshots
from src.safety.safety_guard import check_system_limits
from src.scheduler.tick_scheduler import is_running, start_scheduler, stop_scheduler
from src.sensors.system_sensor import read_system_metrics


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    init_db()
    get_or_create_state()
    start_scheduler()
    yield
    stop_scheduler()


app = FastAPI(title="Digiorg API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Schemas ────────────────────────────────────────────────────────────────────

class DirectiveInput(BaseModel):
    name: str
    description: str
    type: str = "custom"
    threshold: int = 70


class DirectiveStatusInput(BaseModel):
    is_active: bool


# ── Helpers ────────────────────────────────────────────────────────────────────

def _classify_autonomous_action(description: str | None) -> dict | None:
    if description is None:
        return None

    source = "unknown"
    reason = None

    if "survival instinct" in description:
        source = "instinct"
    elif "by directive" in description:
        source = "directive"
        reason = description.split("by directive", 1)[1].strip().rstrip(".")
    elif "LLM reasoning" in description:
        source = "llm"

    return {"source": source, "reason": reason, "description": description}


def _serialize_state(state, directive_list=None, latest_autonomous_event=None) -> dict:
    active_directives = (
        [d.name for d in directive_list if d.is_active]
        if directive_list is not None
        else []
    )

    autonomous_action = (
        _classify_autonomous_action(latest_autonomous_event.description)
        if latest_autonomous_event is not None
        else None
    )

    return {
        "name": state.name,
        "energy": state.energy,
        "hunger": state.hunger,
        "sleepiness": state.sleepiness,
        "hygiene": state.hygiene,
        "mood": state.mood,
        "alive": state.alive,
        "last_tick": state.last_tick.isoformat(),
        "active_directives": active_directives,
        "latest_autonomous_action": (
            {
                "source": autonomous_action["source"],
                "reason": autonomous_action["reason"],
                "description": autonomous_action["description"],
                "created_at": latest_autonomous_event.created_at.isoformat(),
            }
            if latest_autonomous_event is not None and autonomous_action is not None
            else None
        ),
    }


# ── General ────────────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {"message": "Digiorg API active", "docs": "/docs"}


@app.get("/health")
def health():
    return {"status": "ok", "service": "digiorg", "scheduler_running": is_running()}


# ── WebSocket ──────────────────────────────────────────────────────────────────

@app.websocket("/ws")
async def websocket_route(websocket: WebSocket):
    await websocket_endpoint(websocket)


# ── State ──────────────────────────────────────────────────────────────────────

@app.get("/state")
def state():
    current_state = get_or_create_state()
    directive_list = get_directives()
    latest_autonomous_event = get_latest_event_by_type("autonomous_action")
    return _serialize_state(current_state, directive_list, latest_autonomous_event)


# ── Events ─────────────────────────────────────────────────────────────────────

@app.get("/events")
def events(limit: int = 10):
    recent_events = get_recent_events(limit=limit)
    return [
        {
            "id": event.id,
            "event_type": event.event_type,
            "description": event.description,
            "created_at": event.created_at.isoformat(),
        }
        for event in recent_events
    ]


# ── Manual actions ─────────────────────────────────────────────────────────────

@app.post("/action/feed")
def action_feed():
    current_state = get_or_create_state()
    if not current_state.alive:
        raise HTTPException(status_code=409, detail="Digiorg is not alive.")
    state = feed_digiorg()
    return {"message": "Digiorg has eaten.", "energy": state.energy, "hunger": state.hunger, "mood": state.mood}


@app.post("/action/sleep")
def action_sleep():
    current_state = get_or_create_state()
    if not current_state.alive:
        raise HTTPException(status_code=409, detail="Digiorg is not alive.")
    state = put_to_sleep()
    return {"message": "Digiorg has slept.", "energy": state.energy, "sleepiness": state.sleepiness, "mood": state.mood}


@app.post("/action/clean")
def action_clean():
    current_state = get_or_create_state()
    if not current_state.alive:
        raise HTTPException(status_code=409, detail="Digiorg is not alive.")
    state = clean_digiorg()
    return {"message": "Digiorg has been cleaned.", "hygiene": state.hygiene, "mood": state.mood}


@app.post("/action/revive")
def action_revive():
    with SessionLocal() as session:
        state = session.execute(select(VitalState)).scalar_one_or_none()

        if state is None:
            raise HTTPException(status_code=404, detail="No vital state exists.")
        if state.alive:
            raise HTTPException(status_code=409, detail="Digiorg is already alive.")

        state.alive = True
        state.energy = 100
        state.hunger = 0
        state.sleepiness = 0
        state.hygiene = 100
        state.mood = "reborn"
        state.last_tick = datetime.now(timezone.utc)

        session.commit()
        session.refresh(state)
        log_event("revive", "Digiorg has been revived with full vital state.")

    if not is_running():
        start_scheduler()

    return {
        "message": "Digiorg has been revived.",
        "energy": state.energy,
        "hunger": state.hunger,
        "sleepiness": state.sleepiness,
        "hygiene": state.hygiene,
        "mood": state.mood,
        "alive": state.alive,
    }


# ── Body ───────────────────────────────────────────────────────────────────────

@app.get("/body")
def body():
    return build_body_state(get_or_create_state())


# ── Brain ──────────────────────────────────────────────────────────────────────

@app.get("/brain")
def brain():
    current_state = get_or_create_state()
    directive_list = get_directives()
    active_directives = [d for d in directive_list if d.is_active]
    settings = load_settings()

    if not settings["brain"]["llm_enabled"]:
        raise HTTPException(status_code=503, detail="LLM disabled in configuration.")

    prompt = build_decision_prompt(
        state=current_state,
        active_directives=active_directives,
        settings=settings,
    )
    response = query_llm(prompt)

    if response is None:
        raise HTTPException(status_code=503, detail="Ollama not available.")

    action, thought = parse_llm_response(response)

    return {
        "thought": thought,
        "suggested_action": action,
        "state_snapshot": {
            "energy": current_state.energy,
            "hunger": current_state.hunger,
            "sleepiness": current_state.sleepiness,
            "hygiene": current_state.hygiene,
            "mood": current_state.mood,
        },
        "active_directives": [d.name for d in active_directives],
    }


# ── Sensors ────────────────────────────────────────────────────────────────────

@app.get("/sensors")
def sensors():
    return read_system_metrics()


# ── Safety ─────────────────────────────────────────────────────────────────────

@app.get("/safety")
def safety():
    return check_system_limits()


# ── Memory ─────────────────────────────────────────────────────────────────────

@app.get("/memory/snapshots")
def memory_snapshots(limit: int = 50):
    snapshots = get_snapshots(limit=limit)
    return [
        {
            "id": s.id,
            "energy": s.energy,
            "hunger": s.hunger,
            "sleepiness": s.sleepiness,
            "hygiene": s.hygiene,
            "mood": s.mood,
            "alive": s.alive,
            "recorded_at": s.recorded_at.isoformat(),
        }
        for s in snapshots
    ]


@app.get("/memory/patterns")
def memory_patterns():
    patterns = get_latest_patterns()
    return [
        {
            "stat": p.stat,
            "avg_value": p.avg_value,
            "min_value": p.min_value,
            "max_value": p.max_value,
            "trend": p.trend,
            "computed_at": p.computed_at.isoformat(),
        }
        for p in patterns
    ]


@app.post("/memory/patterns/compute")
def memory_compute_patterns():
    patterns = compute_patterns()
    if not patterns:
        raise HTTPException(
            status_code=422,
            detail="Not enough snapshots to compute patterns. Wait for at least 2 snapshots."
        )
    return {"message": f"Patterns computed for {len(patterns)} stats."}


# ── Scheduler ──────────────────────────────────────────────────────────────────

@app.get("/scheduler")
def scheduler_status():
    return {"running": is_running()}


@app.post("/scheduler/start")
def scheduler_start():
    if is_running():
        raise HTTPException(status_code=409, detail="Scheduler is already running.")
    start_scheduler()
    return {"message": "Scheduler started.", "running": is_running()}


@app.post("/scheduler/stop")
def scheduler_stop():
    if not is_running():
        raise HTTPException(status_code=409, detail="Scheduler is not running.")
    stop_scheduler()
    return {"message": "Scheduler stopped.", "running": is_running()}


# ── Directives ─────────────────────────────────────────────────────────────────

@app.get("/directives")
def directives():
    return [
        {
            "id": d.id,
            "name": d.name,
            "description": d.description,
            "type": d.type,
            "threshold": d.threshold,
            "is_active": d.is_active,
            "created_at": d.created_at.isoformat(),
        }
        for d in get_directives()
    ]


@app.get("/directives/types")
def directive_types():
    return {"types": list(DIRECTIVE_TYPES)}


@app.post("/directives")
def create_new_directive(payload: DirectiveInput):
    if payload.type not in DIRECTIVE_TYPES:
        raise HTTPException(
            status_code=422,
            detail=f"Invalid type '{payload.type}'. Valid types: {list(DIRECTIVE_TYPES)}"
        )
    directive = create_directive(
        name=payload.name,
        description=payload.description,
        type=payload.type,
        threshold=payload.threshold,
    )
    return {
        "id": directive.id,
        "name": directive.name,
        "description": directive.description,
        "type": directive.type,
        "threshold": directive.threshold,
        "is_active": directive.is_active,
        "created_at": directive.created_at.isoformat(),
    }


@app.patch("/directives/{name}")
def update_directive_status(name: str, payload: DirectiveStatusInput):
    directive = set_directive_status(name, payload.is_active)
    if directive is None:
        raise HTTPException(status_code=404, detail=f"Directive '{name}' not found.")
    return {
        "id": directive.id,
        "name": directive.name,
        "description": directive.description,
        "type": directive.type,
        "threshold": directive.threshold,
        "is_active": directive.is_active,
        "created_at": directive.created_at.isoformat(),
    }


@app.delete("/directives/{name}")
def delete_existing_directive(name: str):
    deleted = delete_directive(name)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Directive '{name}' not found.")
    return {"message": f"Directive '{name}' deleted successfully."}