from datetime import date

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from racket_tracker.racket_images import DEFAULT_RACKET_IMAGE_ID


class Base(DeclarativeBase):
    pass


class Racket(Base):
    __tablename__ = "rackets"

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(String(100))
    brand: Mapped[str] = mapped_column(String(100), nullable=False, default="")
    model: Mapped[str] = mapped_column(String(100))
    notes: Mapped[str] = mapped_column(Text, nullable=False, default="")
    image_id: Mapped[str] = mapped_column(
        String(50), nullable=False, default=DEFAULT_RACKET_IMAGE_ID
    )

    string_changes: Mapped[list["StringChange"]] = relationship(
        back_populates="racket",
        cascade="all, delete-orphan",
        order_by=lambda: (StringChange.changed_on.desc(), StringChange.id.desc()),
    )

    grip_changes: Mapped[list["GripChange"]] = relationship(
        back_populates="racket",
        cascade="all, delete-orphan",
        order_by=lambda: (GripChange.changed_on.desc(), GripChange.id.desc()),
    )

    @property
    def current_string(self) -> "StringChange | None":
        return self.string_changes[0] if self.string_changes else None

    @property
    def current_grip(self) -> "GripChange | None":
        return self.grip_changes[0] if self.grip_changes else None


class StringChange(Base):
    __tablename__ = "string_changes"

    id: Mapped[int] = mapped_column(primary_key=True)

    racket_id: Mapped[int] = mapped_column(ForeignKey("rackets.id", ondelete="CASCADE"), index=True)

    string: Mapped[str] = mapped_column(String(150))
    gauge: Mapped[str] = mapped_column(String(30), nullable=False, default="")
    changed_on: Mapped[date]
    notes: Mapped[str] = mapped_column(Text, nullable=False, default="")

    racket: Mapped[Racket] = relationship(back_populates="string_changes")


class GripChange(Base):
    __tablename__ = "grip_changes"

    id: Mapped[int] = mapped_column(primary_key=True)

    racket_id: Mapped[int] = mapped_column(ForeignKey("rackets.id", ondelete="CASCADE"), index=True)

    grip: Mapped[str] = mapped_column(String(150))
    color: Mapped[str] = mapped_column(String(50), nullable=False, default="")
    changed_on: Mapped[date]
    notes: Mapped[str] = mapped_column(Text, nullable=False, default="")

    racket: Mapped[Racket] = relationship(back_populates="grip_changes")
