"""Replays the whole Alembic chain against the pre-migration baseline schema and checks that the
result matches the models.

The chain cannot build a database from scratch (its root revision starts with op.add_column on a table
no migration creates), so every database is really built by create_all and the migrations are only ever
run against production. This test gives them a starting point - tests/utils/baseline_schema.sql, the
schema as it stood at commit 86ea019d~1 - and asserts that replaying every revision on top of it
reproduces Base.metadata."""

from pathlib import Path
from typing import Any, Generator
from unittest.mock import patch

import pytest
from alembic import command
from alembic.autogenerate import compare_metadata
from alembic.config import Config
from alembic.runtime.migration import MigrationContext
from sqlalchemy import Engine, create_engine, text
from sqlalchemy_utils import create_database, database_exists, drop_database

from app import models  # noqa: F401  imported so every model is registered on Base.metadata
from app.database import Base, create_db_url

BASELINE_SCHEMA = Path(__file__).parent / "utils" / "baseline_schema.sql"
ALEMBIC_DIRECTORY = Path(__file__).parent.parent / "alembic"


def alembic_config() -> Config:
    """Build a config pointing at the migration scripts.

    File-less on purpose: passing alembic.ini would make env.py call fileConfig() on it and disable the
    loggers the test session has already created."""

    config = Config()
    config.set_main_option("script_location", str(ALEMBIC_DIRECTORY))
    return config


def schema_differences(engine: Engine) -> list:
    """Return alembic's autogenerate diff between the database and the models.
    :param engine: engine of the database to compare"""

    with engine.connect() as connection:
        return compare_metadata(MigrationContext.configure(connection), Base.metadata)


@pytest.fixture(scope="session")
def migration_database(worker_id: str) -> Generator[Engine, Any, None]:
    """Create an empty database for the replay, one per xdist worker.

    Kept separate from the jam_test* databases the rest of the suite uses: this one holds the historical
    schema rather than the current models."""

    name = "jam_migration_test" if worker_id == "master" else f"jam_migration_test_{worker_id}"
    url = create_db_url(name)

    if database_exists(url):
        drop_database(url)
    create_database(url)
    engine = create_engine(url)

    # env.py reads SQLALCHEMY_DATABASE_URL from app.database on every command, so patching the
    # attribute is what redirects alembic here; setting sqlalchemy.url on the config would be ignored.
    with patch("app.database.SQLALCHEMY_DATABASE_URL", url):
        yield engine

    engine.dispose()
    drop_database(url)


@pytest.fixture
def baselined_engine(migration_database: Engine) -> Engine:
    """Reset the database to the pre-migration baseline so each test replays from a known state."""

    with migration_database.begin() as connection:
        connection.execute(text("DROP SCHEMA public CASCADE"))
        connection.execute(text("CREATE SCHEMA public"))
        connection.execute(text(BASELINE_SCHEMA.read_text(encoding="utf-8")))
    return migration_database


class TestMigrations:
    """Tests that the migration chain reproduces the models from the pre-migration baseline."""

    def test_baseline_is_unstamped(self, baselined_engine: Engine) -> None:
        """The baseline predates the chain, so alembic must see it as being at base."""

        with baselined_engine.connect() as connection:
            assert MigrationContext.configure(connection).get_current_revision() is None

    def test_upgrade_reproduces_the_models(self, baselined_engine: Engine) -> None:
        """Upgrading the baseline to head must leave a schema identical to Base.metadata."""

        command.upgrade(alembic_config(), "head")

        differences = schema_differences(baselined_engine)
        assert differences == [], "\n".join(str(difference) for difference in differences)

    def test_downgrade_then_upgrade_reproduces_the_models(self, baselined_engine: Engine) -> None:
        """Every downgrade must be a working inverse: a full round trip must land back on the models."""

        config = alembic_config()
        command.upgrade(config, "head")
        command.downgrade(config, "base")
        command.upgrade(config, "head")

        differences = schema_differences(baselined_engine)
        assert differences == [], "\n".join(str(difference) for difference in differences)
