from src.core.models import VitalState

SYSTEM_PROMPT = """You are the internal brain of Digiorg, a persistent digital organism with vital stats.
Your role is to reason about the organism's current state and decide what action to take.

Absolute rules:
- If energy <= 10 or sleepiness >= 95: you MUST decide "sleep" (survival).
- If hunger >= 90: you MUST decide "feed" (survival).
- Outside those thresholds, reason with your own judgment considering your thought history and active directives.

Available actions: "feed", "sleep", "clean", "none".

Respond ONLY with a JSON object in this exact format, no additional text:
{"action": "none", "thought": "Brief reasoning in first person as Digiorg."}"""


def build_decision_prompt(
    state: VitalState,
    active_directives: list,
    settings: dict,
    recent_thoughts: list[str] | None = None,
) -> str:
    autonomy = settings["autonomy"]

    if active_directives:
        directives_text = "\n".join(
            f"- [{d.type.upper()}] {d.name}: {d.description}"
            + (f" (threshold: {d.threshold})" if d.type != "custom" else "")
            for d in active_directives
        )
    else:
        directives_text = "none"

    thoughts_section = ""
    if recent_thoughts:
        formatted = "\n".join(f"- {t}" for t in recent_thoughts[-3:])
        thoughts_section = f"\nMy recent thoughts:\n{formatted}\n"

    return f"""{SYSTEM_PROMPT}

Current vital state:
- Energy: {state.energy}/100
- Hunger: {state.hunger}/100 (0=full, 100=starving)
- Sleepiness: {state.sleepiness}/100 (0=awake, 100=exhausted)
- Hygiene: {state.hygiene}/100 (0=dirty, 100=clean)
- Mood: {state.mood}
- Alive: {state.alive}

Active user directives:
{directives_text}

Configured thresholds:
- Sleep if sleepiness >= {autonomy["sleep_threshold"]}
- Feed if hunger >= {autonomy["hunger_threshold"]}
- Clean if hygiene <= {autonomy["hygiene_threshold"]}
{thoughts_section}
What do you decide to do now?"""