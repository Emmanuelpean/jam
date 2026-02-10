"""Demo schema setup and initialization."""

import datetime as dt

from sqlalchemy import text
from sqlalchemy.orm import Session

from app import models
from app.database import Base, demo_engine, demo_session_local, engine
from app.job_rating.prompts import seed_ai_prompts


def setup_demo_schema() -> None:
    """Create the demo schema and all tables, then seed required data.
    Called at application startup."""

    # Create the demo schema if it doesn't exist
    with engine.connect() as conn:
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS demo"))
        conn.commit()

    # Create all tables in the demo schema
    Base.metadata.create_all(bind=demo_engine)

    # Seed required data in the demo schema
    db = demo_session_local()
    try:
        seed_demo_ai_prompts(db)
        cleanup_stale_demo_users(db)

    finally:
        db.close()


def seed_demo_ai_prompts(db: Session) -> None:
    """Seed AI prompts in the demo schema if they don't exist."""

    existing = db.query(models.AiSystemPrompt).first()
    if not existing:
        seed_ai_prompts(db)


def cleanup_stale_demo_users(db: Session) -> None:
    """Delete demo users older than 24 hours from the demo schema."""

    cutoff = dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=24)
    stale_users = (
        db.query(models.User).filter(models.User.is_demo.is_(True)).filter(models.User.created_at < cutoff).all()
    )
    for user in stale_users:
        db.delete(user)
    if stale_users:
        db.commit()
