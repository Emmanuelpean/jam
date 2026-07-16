"""Utilities for interacting with the database"""

from pydantic import BaseModel

from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import Session


def upsert(db: Session, table, rows: list[dict | BaseModel], unique_cols: list[str], extra: dict | None = None) -> None:
    """UPSERT rows on (date) or (date, dataset) — re-running for the same day overwrites.
    :param db: Database session
    :param table: SQLAlchemy table to upsert into
    :param rows: List of dicts to upsert
    :param unique_cols: List of columns that uniquely identify a row
    :param extra: Columns merged into every row (e.g. the originating service_log_id)"""

    if not rows:
        return
    dumped = [row.model_dump() if isinstance(row, BaseModel) else dict(row) for row in rows]
    if extra:
        for row in dumped:
            row.update(extra)
    stmt = pg_insert(table).values(dumped)
    excluded = {c: stmt.excluded[c] for c in dumped[0].keys() if c not in unique_cols}
    stmt = stmt.on_conflict_do_update(index_elements=unique_cols, set_=excluded)
    db.execute(stmt)
