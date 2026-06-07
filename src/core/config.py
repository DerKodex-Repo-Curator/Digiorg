from pathlib import Path
import tomllib


BASE_DIR = Path(__file__).resolve().parents[2]
CONFIG_PATH = BASE_DIR / "config" / "settings.toml"


def load_settings() -> dict:
    with CONFIG_PATH.open("rb") as f:
        return tomllib.load(f)