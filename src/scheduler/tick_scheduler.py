import logging
import threading

from src.core.config import load_settings
from src.core.state_manager import update_state_tick
from src.memory.memory_manager import compute_patterns, save_snapshot
from src.safety.safety_guard import check_system_limits

logger = logging.getLogger("digiorg.scheduler")

_scheduler_thread: threading.Thread | None = None
_stop_event = threading.Event()
_tick_count = 0
SNAPSHOT_EVERY = 6    # snapshot cada 6 ticks (30s con tick_seconds=5)
PATTERN_EVERY = 60    # patrones cada 60 ticks (5min con tick_seconds=5)


def _tick_loop() -> None:
    global _tick_count
    settings = load_settings()
    tick_seconds = settings["life"]["tick_seconds"]

    logger.info(f"Scheduler iniciado. Tick cada {tick_seconds}s.")

    while not _stop_event.wait(timeout=tick_seconds):
        try:
            _tick_count += 1

            state = update_state_tick()
            logger.debug(
                f"Tick {_tick_count} — energy={state.energy} hunger={state.hunger} "
                f"sleepiness={state.sleepiness} hygiene={state.hygiene} "
                f"mood={state.mood} alive={state.alive}"
            )

            if not state.alive:
                logger.warning("Digiorg ha muerto. El scheduler sigue activo esperando revive.")

            safety_result = check_system_limits()
            if not safety_result["safe"]:
                for violation in safety_result["violations"]:
                    logger.warning(f"Safety violation: {violation['detail']}")

            if _tick_count % SNAPSHOT_EVERY == 0:
                save_snapshot()
                logger.debug(f"Snapshot guardado en tick {_tick_count}.")

            if _tick_count % PATTERN_EVERY == 0:
                compute_patterns()
                logger.debug(f"Patrones calculados en tick {_tick_count}.")

        except Exception as e:
            logger.exception(f"Error en tick del scheduler: {e}")

    logger.info("Scheduler detenido.")


def start_scheduler() -> None:
    global _scheduler_thread, _stop_event

    if _scheduler_thread is not None and _scheduler_thread.is_alive():
        logger.warning("El scheduler ya está en ejecución.")
        return

    _stop_event.clear()
    _scheduler_thread = threading.Thread(
        target=_tick_loop,
        name="DigiorgScheduler",
        daemon=True,
    )
    _scheduler_thread.start()


def stop_scheduler() -> None:
    global _scheduler_thread

    _stop_event.set()

    if _scheduler_thread is not None:
        _scheduler_thread.join(timeout=10)
        _scheduler_thread = None

    logger.info("Scheduler detenido por solicitud externa.")


def is_running() -> bool:
    return _scheduler_thread is not None and _scheduler_thread.is_alive()