from src.core.models import VitalState

MOOD_AVATAR = {
    "stable":        "( •_•)",
    "uncomfortable": "(ó_ò)",
    "distressed":    "(>_<)",
    "critical":      "(x_x)",
    "relieved":      "( ^_^)",
    "rested":        "( -_-)zzz",
    "fresh":         "( ✿_✿)",
    "reborn":        "( ★_★)",
    "unknown":       "( ?_?)",
}

MOOD_DESCRIPTION = {
    "stable":        "Digiorg is stable and in balance.",
    "uncomfortable": "Digiorg feels some discomfort. Something is off.",
    "distressed":    "Digiorg is distressed. Needs attention.",
    "critical":      "Digiorg is in critical state. Urgent intervention needed.",
    "relieved":      "Digiorg feels relieved after eating.",
    "rested":        "Digiorg is resting peacefully.",
    "fresh":         "Digiorg feels clean and renewed.",
    "reborn":        "Digiorg has been reborn with full energy.",
    "unknown":       "Digiorg's state is undetermined.",
}


def _energy_posture(energy: int) -> str:
    if energy >= 75:   return "upright and active"
    elif energy >= 50: return "slightly hunched"
    elif energy >= 25: return "leaning, with effort"
    else:              return "prostrated, no strength"


def _hunger_expression(hunger: int) -> str:
    if hunger >= 90:   return "writhing with hunger"
    elif hunger >= 70: return "with an empty stomach"
    elif hunger >= 50: return "with mild appetite"
    else:              return "satiated"


def _sleepiness_activity(sleepiness: int) -> str:
    if sleepiness >= 90:   return "on the verge of sleep collapse"
    elif sleepiness >= 70: return "with half-closed eyes"
    elif sleepiness >= 50: return "somewhat drowsy"
    else:                  return "awake and alert"


def _hygiene_appearance(hygiene: int) -> str:
    if hygiene >= 80:   return "clean and presentable"
    elif hygiene >= 60: return "slightly unkempt"
    elif hygiene >= 40: return "dirty and smelly"
    else:               return "in a deplorable state of filth"


def build_body_state(state: VitalState) -> dict:
    mood = state.mood if state.mood in MOOD_AVATAR else "unknown"

    avatar = MOOD_AVATAR[mood]
    mood_description = MOOD_DESCRIPTION[mood]

    posture    = _energy_posture(state.energy)
    expression = _hunger_expression(state.hunger)
    activity   = _sleepiness_activity(state.sleepiness)
    appearance = _hygiene_appearance(state.hygiene)

    physical_description = (
        f"Digiorg appears {posture}, {activity}. "
        f"Its appearance is {appearance} and shows {expression}."
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
        mood_description = "Digiorg has ceased to exist."
        physical_description = "Digiorg's body lies motionless. No vital signs remaining."
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