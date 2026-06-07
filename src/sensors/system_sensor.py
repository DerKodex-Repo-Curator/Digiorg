import psutil

from src.core.config import load_settings


def read_system_metrics() -> dict:
    settings = load_settings()
    safety = settings["safety"]

    cpu_percent = psutil.cpu_percent(interval=0.5)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage("/")

    memory_used_mb = memory.used / (1024 ** 2)

    return {
        "cpu": {
            "percent": cpu_percent,
            "alert": cpu_percent > safety["max_cpu_percent"],
        },
        "memory": {
            "used_mb": round(memory_used_mb, 1),
            "total_mb": round(memory.total / (1024 ** 2), 1),
            "percent": memory.percent,
            "alert": memory_used_mb > safety["max_memory_mb"],
        },
        "disk": {
            "used_gb": round(disk.used / (1024 ** 3), 2),
            "total_gb": round(disk.total / (1024 ** 3), 2),
            "percent": disk.percent,
        },
    }