import os

import flet as ft

from racket_tracker.app import RacketTrackerApp
from racket_tracker.data.database import Database
from racket_tracker.data.repository import RacketRepository
from racket_tracker.dev_seed import seed_demo_data


def main(page: ft.Page) -> None:
    database = Database.from_app_storage()
    database.create_schema()

    if os.getenv("RACKET_TRACKER_DEMO_DATA") == "1":
        seed_demo_data(database)

    app = RacketTrackerApp(
        page=page,
        repository=RacketRepository(database),
    )
    app.mount()


if __name__ == "__main__":
    ft.run(main, assets_dir="assets")
