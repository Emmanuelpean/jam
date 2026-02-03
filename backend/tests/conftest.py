"""
Test configuration and pytest hooks.

Fixtures are organized in the tests/fixtures/ directory:
- database.py: Database session and engine fixtures
- clients.py: API test client fixtures
- users.py: User-related fixtures
- test_data.py: Test data fixtures for various models

The CRUDTestBase class is in tests/utils/crud_test_base.py
"""

import os

import pytest


# Load fixtures from separate modules
pytest_plugins = [
    "tests.fixtures.database",
    "tests.fixtures.clients",
    "tests.fixtures.users",
    "tests.fixtures.test_data",
]


# -------------------------------------------------------- UTILS -------------------------------------------------------


def open_file(filepath: str) -> str:
    """Helper function to open a text file from the resources directory.
    :param filepath: The name of the file located in the resources directory"""

    base_dir = os.path.dirname(__file__)
    filepath = os.path.join(base_dir, "resources", filepath)
    with open(filepath, "r", encoding="utf8") as ofile:
        return ofile.read()


def pytest_configure(config) -> None:
    """Configure pytest to add custom markers."""

    config.addinivalue_line(
        "markers",
        "requires_actions(*actions): mark test as requiring certain CRUD actions",
    )


def pytest_collection_modifyitems(config, items) -> None:
    """Modify collected test items to skip tests based on actions_to_test setting in test classes."""

    _ = config
    for item in items:
        mark = item.get_closest_marker("requires_actions")
        if not mark:
            continue
        required_actions = set(mark.args)
        cls = getattr(item, "cls", None)
        actions_to_test = getattr(cls, "actions_to_test", [])
        if required_actions.isdisjoint(actions_to_test):
            item.add_marker(pytest.mark.skip(reason="Skipping tests as per actions_to_test setting"))
