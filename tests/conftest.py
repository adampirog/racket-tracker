from pathlib import Path

import pytest

from racket_tracker.data.database import Database
from racket_tracker.data.repository import RacketRepository


@pytest.fixture
def database(tmp_path: Path) -> Database:
    database = Database(tmp_path / "test.sqlite3")
    database.create_schema()
    return database


@pytest.fixture
def repository(database: Database) -> RacketRepository:
    return RacketRepository(database)
