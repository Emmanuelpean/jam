"""Utilities for interacting with the database"""

from pydantic import BaseModel

from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import Session


def upsert(db: Session, table, rows: list[dict | BaseModel], unique_cols: list[str]) -> None:
    """UPSERT rows on (date) or (date, dataset) — re-running for the same day overwrites.
    :param db: Database session
    :param table: SQLAlchemy table to upsert into
    :param rows: List of dicts to upsert
    :param unique_cols: List of columns that uniquely identify a row"""

    if not rows:
        return
    if isinstance(rows[0], BaseModel):
        rows = [row.model_dump() for row in rows]
    stmt = pg_insert(table).values(rows)
    excluded = {c: stmt.excluded[c] for c in rows[0].keys() if c not in unique_cols}
    stmt = stmt.on_conflict_do_update(index_elements=unique_cols, set_=excluded)
    db.execute(stmt)
