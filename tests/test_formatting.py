from datetime import date

import pytest

from racket_tracker.formatting import (
    format_active_duration,
    format_date,
    format_elapsed_duration,
    format_gauge,
    format_relative_date,
    format_tension_pair,
)


def test_format_date() -> None:
    assert format_date(date(2026, 10, 5)) == "5 Oct 2026"


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (date(2026, 10, 15), "today"),
        (date(2026, 10, 14), "yesterday"),
        (date(2026, 10, 12), "3 days ago"),
        (date(2026, 10, 8), "1 week ago"),
        (date(2026, 10, 5), "1 week 3 days ago"),
        (date(2026, 10, 1), "2 weeks ago"),
        (date(2026, 9, 15), "1 month ago"),
        (date(2026, 9, 1), "1 month 2 weeks ago"),
        (date(2026, 7, 1), "3 months 2 weeks ago"),
        (date(2026, 5, 1), "5 months 2 weeks ago"),
        (date(2025, 10, 15), "1 year ago"),
        (date(2025, 9, 1), "1 year 1 month ago"),
        (date(2025, 10, 1), "1 year 2 weeks ago"),
        (date(2024, 4, 15), "2 years 6 months ago"),
        (date(2026, 10, 16), "16 Oct 2026"),
    ],
)
def test_format_relative_date(value: date, expected: str) -> None:
    assert format_relative_date(value, today=date(2026, 10, 15)) == expected


@pytest.mark.parametrize(
    ("value", "today", "expected"),
    [
        (date(2026, 10, 15), date(2026, 10, 15), "Active since today"),
        (date(2026, 10, 14), date(2026, 10, 15), "Active for 1 day"),
        (date(2026, 10, 5), date(2026, 10, 15), "Active for 1 week 3 days"),
        (date(2026, 7, 1), date(2026, 10, 15), "Active for 3 months 2 weeks"),
        (date(2025, 9, 1), date(2026, 10, 15), "Active for 1 year 1 month"),
        (date(2026, 10, 16), date(2026, 10, 15), "Active from 16 Oct 2026"),
    ],
)
def test_format_active_duration(value: date, today: date, expected: str) -> None:
    assert format_active_duration(value, today=today) == expected


@pytest.mark.parametrize(
    ("value", "today", "expected"),
    [
        (date(2024, 1, 31), date(2024, 2, 29), "1 month"),
        (date(2024, 2, 29), date(2025, 2, 28), "1 year"),
        (date(2025, 3, 31), date(2025, 4, 30), "1 month"),
    ],
)
def test_elapsed_duration_calendar_boundaries(value: date, today: date, expected: str) -> None:
    assert format_elapsed_duration(value, today=today) == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [(1.10, "1.10 mm"), (1.25, "1.25 mm"), (1.30, "1.30 mm"), (1.40, "1.40 mm")],
)
def test_format_gauge(value: float, expected: str) -> None:
    assert format_gauge(value) == expected


@pytest.mark.parametrize(
    ("mains", "crosses", "expected"),
    [
        (22.0, 21.0, "22/21 kg"),
        (21.5, 20.5, "21.5/20.5 kg"),
    ],
)
def test_format_tension_pair(mains: float, crosses: float, expected: str) -> None:
    assert format_tension_pair(mains, crosses) == expected
