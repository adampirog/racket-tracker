from calendar import monthrange
from datetime import date


def format_tension_pair(mains: float, crosses: float) -> str:
    return f"{mains:g}/{crosses:g} kg"


def format_date(value: date) -> str:
    return value.strftime("%d %b %Y").lstrip("0")


def _add_months(value: date, months: int) -> date:
    """Add calendar months, clamping to the target month's last day."""
    month_index = value.year * 12 + value.month - 1 + months
    year, month_index = divmod(month_index, 12)
    month = month_index + 1

    day = min(value.day, monthrange(year, month)[1])
    return date(year, month, day)


def format_elapsed_duration(value: date, *, today: date | None = None) -> str:
    """Format elapsed time using up to two nonzero calendar units."""
    today = today or date.today()

    if value > today:
        raise ValueError("Cannot format elapsed duration for a future date.")

    months = (today.year - value.year) * 12 + today.month - value.month
    anniversary = _add_months(value, months)

    if anniversary > today:
        months -= 1
        anniversary = _add_months(value, months)

    years, months = divmod(months, 12)
    weeks, days = divmod((today - anniversary).days, 7)

    units = [
        (years, "year"),
        (months, "month"),
        (weeks, "week"),
        (days, "day"),
    ]

    parts = [f"{count} {unit}{'s' if count != 1 else ''}" for count, unit in units if count]

    return " ".join(parts[:2]) if parts else "0 days"


def format_relative_date(value: date, *, today: date | None = None) -> str:
    today = today or date.today()

    if value > today:
        return format_date(value)

    if value == today:
        return "today"

    if (today - value).days == 1:
        return "yesterday"

    return f"{format_elapsed_duration(value, today=today)} ago"


def format_active_duration(value: date, *, today: date | None = None) -> str:
    """Format how long a racket has been active."""
    today = today or date.today()

    if value > today:
        return f"Active from {format_date(value)}"

    if value == today:
        return "Active since today"

    return f"Active for {format_elapsed_duration(value, today=today)}"


def format_gauge(value: float) -> str:
    return f"{value:.2f} mm"
