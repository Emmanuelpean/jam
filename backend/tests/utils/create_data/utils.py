"""Utility functions for creating test data."""

import copy


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


def create_db_entries(db, model, data: list | dict) -> list:
    """Add a list of items to the database and commit
    :param db: database session
    :param model: model class to create entries from
    :param data: list of dictionaries or single dictionary to create entries from
    :return: list of created entries"""

    if isinstance(data, dict):
        data = [data]
    entries = [model(**kwargs) for kwargs in data]
    db.add_all(entries)
    db.commit()
    for item in entries:
        db.refresh(item)
    return entries
