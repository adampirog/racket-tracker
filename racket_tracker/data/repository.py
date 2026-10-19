from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from .database import Database
from .models import GripChange, Racket, StringChange


class RacketRepository:
    def __init__(self, database: Database) -> None:
        self.database = database

    def get_all(self) -> list[Racket]:
        with self.database.session() as session:
            statement = (
                select(Racket)
                .options(
                    selectinload(Racket.string_changes),
                    selectinload(Racket.grip_changes),
                )
                .order_by(Racket.id)
            )

            return list(session.scalars(statement).unique())

    def get(self, racket_id: int) -> Racket | None:
        with self.database.session() as session:
            statement = (
                select(Racket)
                .where(Racket.id == racket_id)
                .options(
                    selectinload(Racket.string_changes),
                    selectinload(Racket.grip_changes),
                )
            )

            return session.scalar(statement)

    def add(self, racket: Racket) -> Racket:
        with self.database.transaction() as session:
            session.add(racket)

        return racket

    def delete(self, racket_id: int) -> None:
        with self.database.transaction() as session:
            racket = session.get(Racket, racket_id)

            if racket is not None:
                session.delete(racket)

    def add_string_change(self, change: StringChange) -> StringChange:
        with self.database.transaction() as session:
            session.add(change)

        return change

    def add_grip_change(self, change: GripChange) -> GripChange:
        with self.database.transaction() as session:
            session.add(change)

        return change

    def update(
        self,
        racket_id: int,
        *,
        name: str,
        model: str,
        image_id: str,
        brand: str = "",
        notes: str = "",
    ) -> None:
        with self.database.transaction() as session:
            racket = session.get(Racket, racket_id)

            if racket is None:
                raise LookupError(f"Racket {racket_id} does not exist.")

            racket.name = name
            racket.brand = brand
            racket.model = model
            racket.notes = notes
            racket.image_id = image_id

    def delete_string_change(self, change_id: int) -> None:
        with self.database.transaction() as session:
            change = session.get(StringChange, change_id)

            if change is None:
                raise LookupError(f"String change {change_id} does not exist.")

            session.delete(change)

    def delete_grip_change(self, change_id: int) -> None:
        with self.database.transaction() as session:
            change = session.get(GripChange, change_id)

            if change is None:
                raise LookupError(f"Grip change {change_id} does not exist.")

            session.delete(change)

    def set_active(self, racket_id: int, *, active_since: date | None = None) -> None:
        with self.database.transaction() as session:
            racket = session.get(Racket, racket_id)

            if racket is None:
                raise LookupError(f"Racket {racket_id} does not exist.")

            statement = select(Racket).where(
                Racket.active_since.is_not(None), Racket.id != racket_id
            )

            for active_racket in session.scalars(statement):
                active_racket.active_since = None

            if racket.active_since is None:
                racket.active_since = active_since or date.today()
