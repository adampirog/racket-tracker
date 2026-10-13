from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Racket:
    id: int
    name: str
    model: str
    brand: str | None = None
