from collections.abc import Callable
from dataclasses import dataclass
from datetime import date, datetime

import flet as ft

from racket_tracker.data.models import Racket
from racket_tracker.formatting import format_date, normalize_gauge


@dataclass(frozen=True, slots=True)
class StringChangeFormValues:
    string: str
    gauge: str
    changed_on: date
    notes: str


@dataclass(frozen=True, slots=True)
class GripChangeFormValues:
    grip: str
    color: str
    changed_on: date
    notes: str


def build_string_change_dialog(
    *,
    racket: Racket,
    show_dialog: Callable[[ft.DialogControl], None],
    on_submit: Callable[[StringChangeFormValues], None],
    on_cancel: Callable[[], None],
) -> ft.AlertDialog:
    current = racket.current_string

    string = ft.TextField(
        label="String",
        hint_text="e.g. Babolat RPM Blast",
        value=current.string if current else "",
        autofocus=True,
        max_length=150,
        capitalization=ft.TextCapitalization.WORDS,
        autocorrect=False,
    )

    gauge = ft.TextField(
        label="Gauge",
        hint_text="1.25",
        value=_current_gauge(racket),
        suffix="mm",
        max_length=10,
        autocorrect=False,
    )

    date_field, get_date = _build_date_field(
        show_dialog=show_dialog,
    )

    notes = _build_notes_field()

    def submit(_: object) -> None:
        string_value = _text(string.value)

        string.error = None
        gauge.error = None

        if not string_value:
            string.error = "String is required"

        try:
            gauge_value = normalize_gauge(gauge.value or "")
        except ValueError:
            gauge.error = "Enter a valid gauge, e.g. 1.25"
            gauge_value = ""

        if string.error or gauge.error:
            return

        on_submit(
            StringChangeFormValues(
                string=string_value,
                gauge=gauge_value,
                changed_on=get_date(),
                notes=_text(notes.value),
            )
        )

    return _build_dialog(
        title="Log string change",
        racket_name=racket.name,
        controls=[string, gauge, date_field, notes],
        on_submit=submit,
        on_cancel=on_cancel,
    )


def build_grip_change_dialog(
    *,
    racket: Racket,
    show_dialog: Callable[[ft.DialogControl], None],
    on_submit: Callable[[GripChangeFormValues], None],
    on_cancel: Callable[[], None],
) -> ft.AlertDialog:
    current = racket.current_grip

    grip = ft.TextField(
        label="Grip",
        hint_text="e.g. Wilson Pro Overgrip",
        value=current.grip if current else "",
        autofocus=True,
        max_length=150,
        capitalization=ft.TextCapitalization.WORDS,
        autocorrect=False,
    )

    color = ft.TextField(
        label="Color",
        hint_text="e.g. White",
        value=current.color if current else "",
        max_length=50,
        capitalization=ft.TextCapitalization.WORDS,
    )

    date_field, get_date = _build_date_field(
        show_dialog=show_dialog,
    )

    notes = _build_notes_field()

    def submit(_: object) -> None:
        grip_value = _text(grip.value)
        grip.error = None

        if not grip_value:
            grip.error = "Grip is required"
            return

        on_submit(
            GripChangeFormValues(
                grip=grip_value,
                color=_text(color.value),
                changed_on=get_date(),
                notes=_text(notes.value),
            )
        )

    return _build_dialog(
        title="Log grip change",
        racket_name=racket.name,
        controls=[grip, color, date_field, notes],
        on_submit=submit,
        on_cancel=on_cancel,
    )


def _build_dialog(
    *,
    title: str,
    racket_name: str,
    controls: list[ft.Control],
    on_submit: Callable[[object], None],
    on_cancel: Callable[[], None],
) -> ft.AlertDialog:
    return ft.AlertDialog(
        modal=True,
        scrollable=True,
        title=ft.Text(title),
        content=ft.Column(
            spacing=12,
            controls=[
                ft.Text(racket_name, weight=ft.FontWeight.BOLD),
                *controls,
            ],
        ),
        actions=[
            ft.TextButton(content="Cancel", on_click=lambda _: on_cancel()),
            ft.Button(content="Save", on_click=on_submit),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )


def _build_date_field(
    *, show_dialog: Callable[[ft.DialogControl], None]
) -> tuple[ft.TextField, Callable[[], date]]:
    selected_date = date.today()

    field = ft.TextField(
        label="Date",
        value=format_date(selected_date),
        read_only=True,
    )

    def select_date(
        event: ft.Event[ft.DatePicker],
    ) -> None:
        nonlocal selected_date

        value = event.control.value

        if value is None:
            return

        selected_date = _as_date(value)
        field.value = format_date(selected_date)

    picker = ft.DatePicker(
        value=selected_date,
        current_date=selected_date,
        last_date=selected_date,
        help_text="When was it changed?",
        on_change=select_date,
        locale=ft.Locale("en", "GB"),
    )

    field.suffix_icon = ft.IconButton(
        icon=ft.Icons.CALENDAR_MONTH, on_click=lambda _: show_dialog(picker)
    )
    field.on_click = lambda _: show_dialog(picker)

    return field, lambda: selected_date


def _current_gauge(racket: Racket) -> str:
    current = racket.current_string

    if current is None or not current.gauge:
        return ""

    try:
        return normalize_gauge(current.gauge)
    except ValueError:
        return ""


def _as_date(value: date | datetime) -> date:
    if isinstance(value, datetime):
        return value.date()

    return value


def _build_notes_field() -> ft.TextField:
    return ft.TextField(
        label="Notes",
        hint_text="Optional",
        multiline=True,
        min_lines=2,
        max_lines=4,
        capitalization=ft.TextCapitalization.SENTENCES,
    )


def _text(value: str | None) -> str:
    return (value or "").strip()
