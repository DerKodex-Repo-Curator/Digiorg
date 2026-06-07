import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.core.database import Base
from src.core.directives import Directive  # noqa: F401
from src.core.events import EventLog  # noqa: F401
from src.core.models import VitalState  # noqa: F401
from src.memory.models import PatternSummary, StateSnapshot  # noqa: F401


TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(scope="function")
def engine():
    _engine = create_engine(TEST_DATABASE_URL, future=True)
    Base.metadata.create_all(bind=_engine)
    yield _engine
    Base.metadata.drop_all(bind=_engine)


@pytest.fixture(scope="function")
def session(engine):
    _session_factory = sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
        future=True,
        expire_on_commit=False,
    )
    with _session_factory() as _session:
        yield _session


@pytest.fixture(scope="function")
def patch_session(session, monkeypatch):
    """Reemplaza SessionLocal en todos los módulos por la sesión de test."""
    from unittest.mock import MagicMock
    import src.core.actions as actions_module
    import src.core.state_manager as state_manager_module
    import src.core.event_manager as event_manager_module
    import src.core.directive_manager as directive_manager_module
    import src.memory.memory_manager as memory_manager_module

    mock_session_factory = MagicMock()
    mock_session_factory.return_value.__enter__ = lambda s, *a: session
    mock_session_factory.return_value.__exit__ = MagicMock(return_value=False)

    for module in [
        actions_module,
        state_manager_module,
        event_manager_module,
        directive_manager_module,
        memory_manager_module,
    ]:
        monkeypatch.setattr(module, "SessionLocal", mock_session_factory)

    return session