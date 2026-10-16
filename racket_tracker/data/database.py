import os
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from sqlalchemy import Engine, create_engine, event
from sqlalchemy.engine.interfaces import DBAPIConnection
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import ConnectionPoolEntry

from .models import Base


DATABASE_FILENAME = "racket_tracker.sqlite3"
SCHEMA_VERSION = 1


class Database:
    def __init__(self, path: Path) -> None:
        self.path = path

        self.engine = create_engine(f"sqlite:///{path}", connect_args={"check_same_thread": False})

        _configure_sqlite(self.engine)

        self._session_factory = sessionmaker(bind=self.engine, expire_on_commit=False)

    @classmethod
    def from_app_storage(cls) -> "Database":
        storage_dir = os.getenv("FLET_APP_STORAGE_DATA")

        if storage_dir is None:
            raise RuntimeError(
                "FLET_APP_STORAGE_DATA is not set. Run the application through Flet."
            )

        return cls(Path(storage_dir) / DATABASE_FILENAME)

    def create_schema(self) -> None:
        Base.metadata.create_all(self.engine)

    @contextmanager
    def session(self) -> Iterator[Session]:
        with self._session_factory() as session:
            yield session

    @contextmanager
    def transaction(self) -> Iterator[Session]:
        with self._session_factory.begin() as session:
            yield session

    def migrate(self) -> None:
        with self.engine.begin() as connection:
            version = connection.exec_driver_sql("PRAGMA user_version").scalar_one()

            if version == 0:
                Base.metadata.create_all(connection)
                connection.exec_driver_sql(f"PRAGMA user_version = {SCHEMA_VERSION}")
                return

            if version > SCHEMA_VERSION:
                raise RuntimeError(
                    f"Database schema {version} is newer than supported schema {SCHEMA_VERSION}."
                )


def _configure_sqlite(engine: Engine) -> None:
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection: DBAPIConnection, _: ConnectionPoolEntry) -> None:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys = ON")
        cursor.close()
