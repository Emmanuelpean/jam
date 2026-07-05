"""Utility functions for creating test data."""

import copy

from sqlalchemy.orm import Session


def override_properties(data: list[dict], *args) -> list[dict]:
    """Override the owner_id in a list of dictionaries
    :param data: list of model entries to override
    :param args: tuples of (key to override, list of models to get new IDs from)"""

    data = copy.deepcopy(data)
    for entry in data:
        for arg in args:
            key, values = arg
            if entry.get(key, None) is not None:
                try:
                    current_id = entry[key] - 1
                    new_id = values[current_id].id
                    entry[key] = new_id
                except IndexError:
                    data.remove(entry)
                    break
    return data


def owner_aligned(users_by_owner_id: dict) -> list:
    """Build a positional user list (index = owner_id - 1) for override_properties, padding gaps with None."""

    return [users_by_owner_id.get(i + 1) for i in range(max(users_by_owner_id))]


def create_db_entries(db: Session, model, data: list | dict | None = None) -> list:
    """Add a list of items to the database and commit
    :param db: database session
    :param model: model class to create entries from
    :param data: list of dictionaries or single dictionary to create entries from
    :return: list of created entries"""

    if not data:
        data = [{}]
    if isinstance(data, dict):
        data = [data]
    entries = [model(**kwargs) for kwargs in data]
    db.add_all(entries)
    db.commit()
    for item in entries:
        db.refresh(item)
    return entries
