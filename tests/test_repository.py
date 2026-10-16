from datetime import date
from pathlib import Path

import pytest
from sqlalchemy import func, select

from racket_tracker.data.database import SCHEMA_VERSION, Database
from racket_tracker.data.models import GripChange, Racket, StringChange
from racket_tracker.data.repository import RacketRepository


def test_add_and_get_racket(repository: RacketRepository) -> None:
    racket = repository.add(Racket(name="Match racket", brand="Babolat", model="Pure Drive"))

    loaded = repository.get(racket.id)

    assert loaded is not None
    assert loaded.name == "Match racket"
    assert loaded.model == "Pure Drive"


def test_current_equipment_is_latest_change(repository: RacketRepository) -> None:
    racket = repository.add(
        Racket(
            name="Match racket",
            model="Pure Drive",
        )
    )

    repository.add_string_change(
        StringChange(
            racket_id=racket.id,
            string="Hyper-G",
            changed_on=date(2026, 9, 1),
        )
    )
    repository.add_string_change(
        StringChange(
            racket_id=racket.id,
            string="RPM Blast",
            changed_on=date(2026, 10, 1),
        )
    )
    repository.add_grip_change(
        GripChange(
            racket_id=racket.id,
            grip="Wilson Pro Overgrip",
            changed_on=date(2026, 9, 20),
        )
    )

    loaded = repository.get(racket.id)

    assert loaded is not None
    assert loaded.current_string is not None
    assert loaded.current_string.string == "RPM Blast"
    assert loaded.current_grip is not None
    assert loaded.current_grip.grip == "Wilson Pro Overgrip"


def test_get_all_keeps_rackets_separate(repository: RacketRepository) -> None:
    repository.add(Racket(name="Match", model="Pure Drive"))
    repository.add(Racket(name="Backup", model="Pure Drive"))

    rackets = repository.get_all()

    assert [racket.name for racket in rackets] == ["Match", "Backup"]
    assert rackets[0].id != rackets[1].id


def test_delete_racket_removes_its_history(
    database: Database, repository: RacketRepository
) -> None:
    racket = repository.add(Racket(name="Match", model="Pure Drive"))

    repository.add_string_change(
        StringChange(racket_id=racket.id, string="RPM Blast", changed_on=date(2026, 10, 1))
    )

    repository.delete(racket.id)

    assert repository.get(racket.id) is None

    with database.session() as session:
        string_changes = session.scalar(select(func.count()).select_from(StringChange))

    assert string_changes == 0


def test_update_racket(repository: RacketRepository) -> None:
    racket = repository.add(
        Racket(name="Old name", brand="Babolat", model="Pure Drive", image_id="aero")
    )

    repository.update(
        racket.id,
        name="Match racket",
        brand="Head",
        model="Radical MP",
        image_id="gravity",
        notes="Main racket",
    )

    loaded = repository.get(racket.id)

    assert loaded is not None
    assert (loaded.name, loaded.brand, loaded.model, loaded.image_id, loaded.notes) == (
        "Match racket",
        "Head",
        "Radical MP",
        "gravity",
        "Main racket",
    )


def test_latest_change_uses_id_as_tiebreaker(repository: RacketRepository) -> None:
    racket = repository.add(Racket(name="Match", model="Pure Drive"))
    changed_on = date(2026, 10, 15)

    repository.add_string_change(
        StringChange(racket_id=racket.id, string="Old string", changed_on=changed_on)
    )
    repository.add_string_change(
        StringChange(racket_id=racket.id, string="New string", changed_on=changed_on)
    )

    repository.add_grip_change(
        GripChange(racket_id=racket.id, grip="Old grip", changed_on=changed_on)
    )
    repository.add_grip_change(
        GripChange(racket_id=racket.id, grip="New grip", changed_on=changed_on)
    )

    loaded = repository.get(racket.id)

    assert loaded is not None
    assert loaded.current_string is not None
    assert loaded.current_string.string == "New string"
    assert loaded.current_grip is not None
    assert loaded.current_grip.grip == "New grip"


def test_update_missing_racket_raises(repository: RacketRepository) -> None:
    with pytest.raises(LookupError):
        repository.update(999, name="Missing", model="Missing", image_id="tfight")


def test_database_survives_restart(tmp_path: Path) -> None:
    path = tmp_path / "racket_tracker.sqlite3"

    first = Database(path)
    first.create_schema()
    first_repository = RacketRepository(first)

    racket = first_repository.add(Racket(name="Match racket", model="Pure Drive", image_id="aero"))
    first_repository.add_string_change(
        StringChange(racket_id=racket.id, string="RPM Blast", changed_on=date(2026, 10, 16))
    )

    first.engine.dispose()

    second = Database(path)
    second.create_schema()
    second_repository = RacketRepository(second)

    loaded = second_repository.get(racket.id)

    assert loaded is not None
    assert loaded.name == "Match racket"
    assert loaded.current_string is not None
    assert loaded.current_string.string == "RPM Blast"


def test_database_is_initialized_at_current_schema(tmp_path: Path) -> None:
    database = Database(tmp_path / "test.sqlite3")
    database.migrate()

    with database.engine.connect() as connection:
        version = connection.exec_driver_sql("PRAGMA user_version").scalar_one()

    assert version == SCHEMA_VERSION
