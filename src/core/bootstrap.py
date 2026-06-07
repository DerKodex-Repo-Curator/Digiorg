from src.core.database import Base, engine
from src.core.directives import Directive  # noqa: F401
from src.core.events import EventLog  # noqa: F401
from src.core.models import VitalState  # noqa: F401
from src.memory.models import PatternSummary, StateSnapshot  # noqa: F401


def init_db() -> None:
    Base.metadata.create_all(bind=engine)