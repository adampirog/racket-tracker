from collections.abc import Callable
from dataclasses import dataclass
from datetime import date, datetime

import flet as ft

from racket_tracker.formatting import format_date


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
    racket_name: str,
    show_dialog: Callable[[ft.DialogControl], None],
    on_submit: Callable[[StringChangeFormValues], None],
    on_cancel: Callable[[], None],
) -> ft.AlertDialog:
    string = ft.TextField(
        label="String",
        hint_text="e.g. Babolat RPM Blast",
        autofocus=True,
        max_length=150,
    )
    gauge = ft.TextField(
        label="Gauge",
        hint_text="e.g. 1.25 mm",
        max_length=30,
    )
    date_field, get_date = _build_date_field(
        show_dialog=show_dialog,
    )
    notes = _build_notes_field()

    def submit(_: object) -> None:
        string_value = (string.value or "").strip()
        string.error = None

        if not string_value:
            string.error = "String is required"
            return

        on_submit(
            StringChangeFormValues(
                string=string_value,
                gauge=_text(gauge.value),
                changed_on=get_date(),
                notes=_text(notes.value),
            )
        )

    return _build_dialog(
        title="Log string change",
        racket_name=racket_name,
        controls=[string, gauge, date_field, notes],
        on_submit=submit,
        on_cancel=on_cancel,
    )


def build_grip_change_dialog(
    *,
    racket_name: str,
    show_dialog: Callable[[ft.DialogControl], None],
    on_submit: Callable[[GripChangeFormValues], None],
    on_cancel: Callable[[], None],
) -> ft.AlertDialog:
    grip = ft.TextField(
        label="Grip",
        hint_text="e.g. Wilson Pro Overgrip",
        autofocus=True,
        max_length=150,
    )
    color = ft.TextField(
        label="Color",
        hint_text="e.g. White",
        max_length=50,
    )
    date_field, get_date = _build_date_field(
        show_dialog=show_dialog,
    )
    notes = _build_notes_field()

    def submit(_: object) -> None:
        grip_value = (grip.value or "").strip()
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
        racket_name=racket_name,
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

    field = ft.TextField(label="Date", value=format_date(selected_date), read_only=True)

    def select_date(event: ft.Event[ft.DatePicker]) -> None:
        nonlocal selected_date

        value = event.control.value

        if value is None:
            return

        selected_date = _as_date(value)
        field.value = format_date(selected_date)

    picker = ft.DatePicker(value=selected_date, current_date=date.today(), on_change=select_date)

    field.suffix_icon = ft.IconButton(
        icon=ft.Icons.CALENDAR_MONTH, on_click=lambda _: show_dialog(picker)
    )
    field.on_click = lambda _: show_dialog(picker)

    return field, lambda: selected_date


def _as_date(value: date | datetime) -> date:
    if isinstance(value, datetime):
        return value.date()

    return value


def _build_notes_field() -> ft.TextField:
    return ft.TextField(
        label="Notes", hint_text="Optional", multiline=True, min_lines=2, max_lines=4
    )


def _text(value: str | None) -> str:
    return (value or "").strip()
