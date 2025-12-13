"""Utility functions and constants for test data management."""

import datetime as dt
import random

from tests.utils.test_data.test_files import load_all_resource_files

RESOURCE_FILES = load_all_resource_files()
random.seed(153625)

CURRENT_DATE = dt.datetime.now(dt.timezone.utc)
DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S%z"
DATE_FORMAT = "%Y-%m-%d"


def add_mappings(
    primary_data: list,
    secondary_data: list,
    mapping_data: list,
    primary_key: str,
    secondary_key: str,
    relationship_attr: str,
) -> None:
    """Generic function to add many-to-many relationships between data objects.
    :param primary_data: List of primary objects (e.g. jobs, interviews)
    :param secondary_data: List of secondary objects (e.g. keywords, persons)
    :param mapping_data: List of mapping dictionaries
    :param primary_key: Key name for primary object ID in mapping (e.g. "job_id", "interview_id")
    :param secondary_key: Key name for secondary object IDs in mapping (e.g. "keyword_ids", "person_ids")
    :param relationship_attr: Attribute name on a primary object for the relationship (e.g. "keywords", "contacts")"""

    for mapping in mapping_data:
        primary_obj = primary_data[mapping[primary_key] - 1]  # Convert to 0-based index
        secondary_ids = mapping[secondary_key]

        for secondary_id in secondary_ids:
            secondary_obj = secondary_data[secondary_id - 1]  # Convert to 0-based index
            getattr(primary_obj, relationship_attr).append(secondary_obj)
