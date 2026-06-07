import logging
import logging.handlers
from pathlib import Path

from src.core.config import load_settings


def setup_logging() -> None:
    settings = load_settings()
    logs_dir = Path(settings["paths"]["logs_dir"])
    logs_dir.mkdir(parents=True, exist_ok=True)

    log_format = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Handler rotativo — máximo 5 MB por archivo, 3 backups
    file_handler = logging.handlers.RotatingFileHandler(
        filename=logs_dir / "digiorg.log",
        maxBytes=5 * 1024 * 1024,
        backupCount=3,
        encoding="utf-8",
    )
    file_handler.setFormatter(log_format)
    file_handler.setLevel(logging.DEBUG)

    # Handler de consola
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_format)
    console_handler.setLevel(logging.INFO)

    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

    logging.getLogger("digiorg").info("Sistema de logging iniciado.")