from src.core.models import VitalState


SYSTEM_PROMPT = """Eres el cerebro interno de Digiorg, un organismo digital con estado vital persistente.
Tu función es razonar sobre el estado actual del organismo y decidir qué acción tomar.

Reglas absolutas:
- Si energy <= 10 o sleepiness >= 95: DEBES decidir "sleep" (supervivencia).
- Si hunger >= 90: DEBES decidir "feed" (supervivencia).
- Fuera de esos umbrales, razona con criterio propio considerando tu historial de pensamientos.

Acciones disponibles: "feed", "sleep", "clean", "none".

Responde ÚNICAMENTE con un objeto JSON con este formato exacto, sin texto adicional:
{"action": "none", "thought": "Razonamiento breve en primera persona como Digiorg."}"""


def build_decision_prompt(
    state: VitalState,
    active_directives: list[str],
    settings: dict,
    recent_thoughts: list[str] | None = None,
) -> str:
    autonomy = settings["autonomy"]

    directives_text = (
        ", ".join(active_directives) if active_directives else "ninguna"
    )

    thoughts_section = ""
    if recent_thoughts:
        formatted = "\n".join(f"- {t}" for t in recent_thoughts[-3:])
        thoughts_section = f"\nMis últimos pensamientos:\n{formatted}\n"

    return f"""{SYSTEM_PROMPT}

Estado vital actual:
- Energía: {state.energy}/100
- Hambre: {state.hunger}/100 (0=saciado, 100=hambre extrema)
- Somnolencia: {state.sleepiness}/100 (0=despierto, 100=agotado)
- Higiene: {state.hygiene}/100 (0=sucio, 100=limpio)
- Humor: {state.mood}
- Vivo: {state.alive}

Directivas activas del usuario: {directives_text}

Umbrales configurados:
- Dormir si somnolencia >= {autonomy["sleep_threshold"]}
- Comer si hambre >= {autonomy["hunger_threshold"]}
- Limpiar si higiene <= {autonomy["hygiene_threshold"]}
{thoughts_section}
¿Qué decides hacer ahora?"""