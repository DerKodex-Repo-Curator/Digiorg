from src.core.models import VitalState


MOOD_AVATAR = {
    "stable":       "( •_•)",
    "uncomfortable": "(ó_ò)",
    "distressed":   "(>_<)",
    "critical":     "(x_x)",
    "relieved":     "( ^_^)",
    "rested":       "( -_-)zzz",
    "fresh":        "( ✿_✿)",
    "reborn":       "( ★_★)",
    "unknown":      "( ?_?)",
}

MOOD_DESCRIPTION = {
    "stable":        "Digiorg se encuentra estable y en equilibrio.",
    "uncomfortable": "Digiorg siente cierta incomodidad. Algo no está bien.",
    "distressed":    "Digiorg está angustiado. Necesita atención.",
    "critical":      "Digiorg está en estado crítico. Intervención urgente.",
    "relieved":      "Digiorg siente alivio tras haber comido.",
    "rested":        "Digiorg descansa plácidamente.",
    "fresh":         "Digiorg se siente limpio y renovado.",
    "reborn":        "Digiorg ha renacido con energía plena.",
    "unknown":       "El estado de Digiorg es indeterminado.",
}


def _energy_posture(energy: int) -> str:
    if energy >= 75:
        return "erguido y activo"
    elif energy >= 50:
        return "ligeramente encorvado"
    elif energy >= 25:
        return "apoyado, con esfuerzo"
    else:
        return "postrado, sin fuerzas"


def _hunger_expression(hunger: int) -> str:
    if hunger >= 90:
        return "retorcido de hambre"
    elif hunger >= 70:
        return "con el estómago vacío"
    elif hunger >= 50:
        return "con ligero apetito"
    else:
        return "saciado"


def _sleepiness_activity(sleepiness: int) -> str:
    if sleepiness >= 90:
        return "al borde del colapso por sueño"
    elif sleepiness >= 70:
        return "con los ojos entrecerrados"
    elif sleepiness >= 50:
        return "algo adormilado"
    else:
        return "despierto y alerta"


def _hygiene_appearance(hygiene: int) -> str:
    if hygiene >= 80:
        return "limpio y presentable"
    elif hygiene >= 60:
        return "algo descuidado"
    elif hygiene >= 40:
        return "sucio y maloliente"
    else:
        return "en un estado deplorable de suciedad"


def build_body_state(state: VitalState) -> dict:
    mood = state.mood if state.mood in MOOD_AVATAR else "unknown"

    avatar = MOOD_AVATAR[mood]
    mood_description = MOOD_DESCRIPTION[mood]

    posture = _energy_posture(state.energy)
    expression = _hunger_expression(state.hunger)
    activity = _sleepiness_activity(state.sleepiness)
    appearance = _hygiene_appearance(state.hygiene)

    physical_description = (
        f"Digiorg aparece {posture}, {activity}. "
        f"Su aspecto es {appearance} y se muestra {expression}."
    )

    vitality_score = round(
        (state.energy * 0.4)
        + ((100 - state.hunger) * 0.3)
        + ((100 - state.sleepiness) * 0.2)
        + (state.hygiene * 0.1),
        1,
    )

    if not state.alive:
        avatar = "(✝_✝)"
        mood_description = "Digiorg ha dejado de existir."
        physical_description = "El cuerpo de Digiorg yace inmóvil. Ya no hay signos vitales."
        vitality_score = 0.0

    return {
        "avatar": avatar,
        "mood_description": mood_description,
        "physical": {
            "posture": posture,
            "activity": activity,
            "appearance": appearance,
            "hunger_state": expression,
            "description": physical_description,
        },
        "vitality_score": vitality_score,
        "alive": state.alive,
    }