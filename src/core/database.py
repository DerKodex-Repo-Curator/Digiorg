from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from src.core.config import load_settings


settings = load_settings()
db_path = Path(settings["paths"]["db_path"])

db_path.parent.mkdir(parents=True, exist_ok=True)

DATABASE_URL = f"sqlite:///{db_path}"

engine = create_engine(DATABASE_URL, echo=False, future=True)
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    future=True,
    expire_on_commit=False,
)
Base = declarative_base()