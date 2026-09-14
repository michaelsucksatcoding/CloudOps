"""Database configuration and session management."""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from services.api.app.config import settings


class Base(DeclarativeBase):
    """Base declarative model for SQLAlchemy entities."""

    pass


# Normalize database URL for SQLAlchemy 2.0 with psycopg
db_url = settings.database_url
if db_url.startswith("postgresql://") and not db_url.startswith(
    "postgresql+psycopg://"
):
    # Allow psycopg (v3) compatibility if specified
    db_url = db_url.replace("postgresql://", "postgresql+psycopg://", 1)

# Configure connection arguments (e.g. check_same_thread for sqlite)
connect_args = {}
if db_url.startswith("sqlite"):
    connect_args["check_same_thread"] = False

engine = create_engine(
    db_url,
    pool_pre_ping=True,
    connect_args=connect_args,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def get_db() -> Generator[Session, None, None]:
    """Provide a transactional database session scope."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
