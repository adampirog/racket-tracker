from collections.abc import Iterable
from dataclasses import dataclass

from racket_tracker.models import GripChange, Racket, StringChange


@dataclass(frozen=True, slots=True)
class RacketState:
    racket: Racket
    current_string: StringChange | None
    current_grip: GripChange | None


def build_racket_state(
    racket: Racket,
    string_changes: Iterable[StringChange],
    grip_changes: Iterable[GripChange],
) -> RacketState:
    current_string = _latest_for_racket(racket.id, string_changes)
    current_grip = _latest_for_racket(racket.id, grip_changes)

    return RacketState(racket=racket, current_string=current_string, current_grip=current_grip)


def _latest_for_racket[T: StringChange | GripChange](
    racket_id: int, changes: Iterable[T]
) -> T | None:
    matching_changes = (change for change in changes if change.racket_id == racket_id)

    return max(matching_changes, key=lambda change: change.changed_on, default=None)
