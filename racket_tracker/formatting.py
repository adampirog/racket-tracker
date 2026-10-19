from datetime import date
from decimal import Decimal, InvalidOperation


def format_tension_pair(mains: float, crosses: float) -> str:
    return f"{mains:g}/{crosses:g} kg"


def format_date(value: date) -> str:
    return value.strftime("%d %b %Y").lstrip("0")


def format_relative_date(value: date, *, today: date | None = None) -> str:
    today = today or date.today()
    days = (today - value).days

    if days < 0:
        return format_date(value)

    if days == 0:
        return "today"

    if days == 1:
        return "yesterday"

    if days < 7:
        return f"{days} days ago"

    if days < 14:
        return "1 week ago"

    if days < 30:
        return f"{days // 7} weeks ago"

    if days < 60:
        return "1 month ago"

    if days < 365:
        return f"{days // 30} months ago"

    if days < 730:
        return "1 year ago"

    return f"{days // 365} years ago"


def normalize_gauge(value: str) -> str:
    value = value.strip().lower()

    if value.endswith("mm"):
        value = value[:-2].strip()

    value = value.replace(",", ".")

    if not value:
        return ""

    try:
        gauge = Decimal(value)
    except InvalidOperation as exc:
        raise ValueError("Invalid gauge") from exc

    if not gauge.is_finite() or gauge <= 0:
        raise ValueError("Invalid gauge")

    normalized = format(gauge.normalize(), "f")

    if "." not in normalized:
        return f"{normalized}.00"

    whole, fraction = normalized.split(".", maxsplit=1)

    if len(fraction) == 1:
        return f"{whole}.{fraction}0"

    return normalized


def format_gauge(value: str) -> str:
    if not value:
        return ""

    try:
        return f"{normalize_gauge(value)} mm"
    except ValueError:
        # Keeps legacy/dev data displayable.
        value = value.strip()
        return value if value.lower().endswith("mm") else f"{value} mm"
