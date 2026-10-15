from datetime import date


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
