"""
Script de arranque manual para debug sin API.
En producción usar: uvicorn src.interface.api:app
"""
from time import sleep

from src.core.bootstrap import init_db
from src.core.config import load_settings
from src.core.state_manager import get_or_create_state, update_state_tick


def print_state(state) -> None:
    print(
        f"[{state.last_tick.isoformat()}] "
        f"alive={state.alive} "
        f"energy={state.energy} "
        f"hunger={state.hunger} "
        f"sleepiness={state.sleepiness} "
        f"hygiene={state.hygiene} "
        f"mood={state.mood}"
    )


def main() -> None:
    settings = load_settings()
    tick_seconds = settings["life"]["tick_seconds"]

    init_db()

    state = get_or_create_state()
    print("Digiorg iniciado en modo debug (sin API).")
    print_state(state)

    while True:
        state = update_state_tick()
        print_state(state)
        sleep(tick_seconds)


if __name__ == "__main__":
    main()