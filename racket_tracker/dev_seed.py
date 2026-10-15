from datetime import date

from sqlalchemy import func, select

from racket_tracker.data.database import Database
from racket_tracker.data.models import GripChange, Racket, StringChange


def seed_demo_data(database: Database) -> None:
    with database.transaction() as session:
        racket_count = session.scalar(select(func.count()).select_from(Racket))

        if racket_count:
            return

        match_racket = Racket(
            name="Match racket",
            brand="Babolat",
            model="Pure Drive (2021)",
        )

        backup_racket = Racket(
            name="Backup racket",
            brand="Babolat",
            model="Pure Drive (2021)",
        )

        radical = Racket(
            name="Radical",
            brand="Head",
            model="Radical MP (2023)",
        )

        session.add_all(
            [
                match_racket,
                backup_racket,
                radical,
            ]
        )

        session.flush()

        session.add_all(
            [
                StringChange(
                    racket_id=match_racket.id,
                    string="Babolat RPM Blast",
                    gauge="1.25 mm",
                    changed_on=date(2026, 10, 8),
                ),
                GripChange(
                    racket_id=match_racket.id,
                    grip="Wilson Pro Overgrip",
                    color="White",
                    changed_on=date(2026, 10, 1),
                ),
                StringChange(
                    racket_id=backup_racket.id,
                    string="Head Lynx Tour",
                    gauge="1.25 mm",
                    changed_on=date(2026, 9, 15),
                ),
            ]
        )
