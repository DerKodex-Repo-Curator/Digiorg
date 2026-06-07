import json
import logging
import urllib.request
from urllib.error import URLError, HTTPError

from src.core.config import load_settings

logger = logging.getLogger("digiorg.brain.llm")


def query_llm(prompt: str) -> str | None:
    settings = load_settings()
    brain = settings["brain"]

    if not brain["llm_enabled"]:
        return None

    host = brain["llm_host"]
    model = brain["llm_model"]
    timeout = brain["llm_timeout_seconds"]
    max_tokens = brain["llm_max_tokens"]

    payload = json.dumps({
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "num_predict": max_tokens,
            "temperature": 0.4,
        },
    }).encode("utf-8")

    url = f"{host}/api/generate"

    try:
        req = urllib.request.Request(
            url,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=timeout) as response:
            body = json.loads(response.read().decode("utf-8"))
            return body.get("response", "").strip()

    except (URLError, HTTPError) as e:
        logger.warning(f"Ollama no disponible: {e}. Usando lógica determinista.")
        return None
    except Exception as e:
        logger.exception(f"Error inesperado en LLM client: {e}")
        return None