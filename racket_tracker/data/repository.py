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
        self, racket_id: int, *, name: str, model: str, brand: str = "", notes: str = ""
    ) -> None:
        with self.database.transaction() as session:
            racket = session.get(Racket, racket_id)

            if racket is None:
                raise LookupError(f"Racket {racket_id} does not exist.")

            racket.name = name
            racket.brand = brand
            racket.model = model
            racket.notes = notes
