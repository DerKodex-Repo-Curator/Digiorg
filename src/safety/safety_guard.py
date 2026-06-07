import logging
from datetime import datetime, timezone

from src.core.config import load_settings
from src.core.event_manager import log_event
from src.sensors.system_sensor import read_system_metrics

logger = logging.getLogger("digiorg.safety")

_last_alert: dict[str, datetime] = {}
ALERT_COOLDOWN_SECONDS = 300  # máximo un log cada 5 minutos por tipo


def _should_log_alert(alert_type: str) -> bool:
    now = datetime.now(timezone.utc)
    last = _last_alert.get(alert_type)
    if last is None or (now - last).total_seconds() >= ALERT_COOLDOWN_SECONDS:
        _last_alert[alert_type] = now
        return True
    return False


def check_system_limits() -> dict:
    settings = load_settings()
    safety = settings["safety"]
    metrics = read_system_metrics()

    violations = []

    if metrics["cpu"]["alert"]:
        msg = (
            f"Alerta de CPU: {metrics['cpu']['percent']}% "
            f"supera el límite de {safety['max_cpu_percent']}%."
        )
        logger.warning(msg)
        if _should_log_alert("cpu"):
            log_event("safety_alert", msg)
        violations.append({"type": "cpu", "detail": msg})

    if metrics["memory"]["alert"]:
        msg = (
            f"Alerta de memoria: {metrics['memory']['used_mb']} MB "
            f"supera el límite de {safety['max_memory_mb']} MB."
        )
        logger.warning(msg)
        if _should_log_alert("memory"):
            log_event("safety_alert", msg)
        violations.append({"type": "memory", "detail": msg})

    return {
        "violations": violations,
        "safe": len(violations) == 0,
        "metrics": metrics,
        "limits": {
            "max_cpu_percent": safety["max_cpu_percent"],
            "max_memory_mb": safety["max_memory_mb"],
            "internet_enabled": safety["internet_enabled"],
            "system_write_enabled": safety["system_write_enabled"],
        },
    }


def is_internet_allowed() -> bool:
    settings = load_settings()
    return settings["safety"]["internet_enabled"]


def is_system_write_allowed() -> bool:
    settings = load_settings()
    return settings["safety"]["system_write_enabled"]


def assert_internet_allowed() -> None:
    if not is_internet_allowed():
        raise PermissionError("Acceso a internet deshabilitado por política de seguridad.")


def assert_system_write_allowed() -> None:
    if not is_system_write_allowed():
        raise PermissionError("Escritura en sistema deshabilitada por política de seguridad.")