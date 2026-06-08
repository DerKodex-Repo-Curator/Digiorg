from sqlalchemy import select

from src.core.database import SessionLocal
from src.core.directives import Directive
from src.core.event_manager import log_event


def create_directive(
    name: str,
    description: str,
    type: str = "custom",
    threshold: int = 70,
) -> Directive:
    with SessionLocal() as session:
        existing = session.execute(
            select(Directive).where(Directive.name == name)
        ).scalar_one_or_none()

        if existing is not None:
            return existing

        directive = Directive(
            name=name,
            description=description,
            type=type,
            threshold=threshold,
            is_active=True,
        )
        session.add(directive)
        session.commit()
        session.refresh(directive)

        log_event("directive_created", f"Directive created: {name} (type={type})")
        return directive


def get_directives() -> list[Directive]:
    with SessionLocal() as session:
        result = session.execute(select(Directive).order_by(Directive.id.asc()))
        return list(result.scalars().all())


def set_directive_status(name: str, is_active: bool) -> Directive | None:
    with SessionLocal() as session:
        directive = session.execute(
            select(Directive).where(Directive.name == name)
        ).scalar_one_or_none()

        if directive is None:
            return None

        directive.is_active = is_active
        session.commit()
        session.refresh(directive)

        status = "activated" if is_active else "deactivated"
        log_event("directive_updated", f"Directive {status}: {name}")
        return directive


def delete_directive(name: str) -> bool:
    with SessionLocal() as session:
        directive = session.execute(
            select(Directive).where(Directive.name == name)
        ).scalar_one_or_none()

        if directive is None:
            return False

        session.delete(directive)
        session.commit()

        log_event("directive_deleted", f"Directive deleted: {name}")
        return True