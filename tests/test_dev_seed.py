from racket_tracker.data.database import Database
from racket_tracker.data.repository import RacketRepository
from racket_tracker.dev_seed import seed_demo_data


def test_demo_seed_is_idempotent(database: Database) -> None:
    seed_demo_data(database)
    seed_demo_data(database)

    rackets = RacketRepository(database).get_all()

    assert len(rackets) == 3
    assert [racket.name for racket in rackets] == ["Match racket", "Backup racket", "Radical"]
