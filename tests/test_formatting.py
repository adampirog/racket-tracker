from datetime import date

import pytest

from racket_tracker.formatting import format_date, format_relative_date


def test_format_date() -> None:
    assert format_date(date(2026, 10, 5)) == "5 Oct 2026"


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (date(2026, 10, 15), "today"),
        (date(2026, 10, 14), "yesterday"),
        (date(2026, 10, 12), "3 days ago"),
        (date(2026, 10, 8), "1 week ago"),
        (date(2026, 10, 1), "2 weeks ago"),
        (date(2026, 9, 1), "1 month ago"),
        (date(2026, 5, 1), "5 months ago"),
        (date(2025, 10, 15), "1 year ago"),
    ],
)
def test_format_relative_date(value: date, expected: str) -> None:
    assert format_relative_date(value, today=date(2026, 10, 15)) == expected
