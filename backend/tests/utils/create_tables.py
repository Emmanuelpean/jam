"""Database schema creation script for setting up an empty database.
Companion to seed_database.py: it creates the tables but inserts no data, and never drops anything."""

from pathlib import Path

from sqlalchemy import inspect

from app import models  # noqa: F401  imported so every model is registered on Base.metadata
from app.database import Base, engine

ALEMBIC_DIRECTORY = Path(__file__).parent.parent.parent / "alembic"


def stamp_alembic_head() -> None:
    """Record the latest revision so a later `alembic upgrade head` applies only the new migrations.

    Alembic is a dev-only dependency, hence the local import. The Config is deliberately file-less:
    passing alembic.ini would make env.py call fileConfig() on it and reconfigure the app's loggers."""

    from alembic import command
    from alembic.config import Config

    config = Config()
    config.set_main_option("script_location", str(ALEMBIC_DIRECTORY))
    command.stamp(config, "head")


def create_tables() -> None:
    """Create every table missing from the database and stamp it at the Alembic head."""

    existing = inspect(engine).get_table_names()
    if existing:
        print(f"{len(existing)} table(s) already exist, creating the missing ones only...")
    else:
        print("Creating all tables from models...")

    Base.metadata.create_all(bind=engine)
    created = sorted(set(inspect(engine).get_table_names()) - set(existing))
    print(f"Created {len(created)} table(s).")

    if "alembic_version" in existing:
        print("Database already stamped, leaving alembic_version untouched.")
    else:
        stamp_alembic_head()
        print("Stamped the database at the Alembic head.")


if __name__ == "__main__":
    create_tables()
