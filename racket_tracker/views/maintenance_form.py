from collections.abc import Callable
from dataclasses import dataclass
from datetime import date, datetime

import flet as ft

from racket_tracker.data.models import Racket
from racket_tracker.formatting import format_date


@dataclass(frozen=True, slots=True)
class StringChangeFormValues:
    string: str
    gauge: float
    mains_tension: float
    crosses_tension: float
    changed_on: date
    notes: str


@dataclass(frozen=True, slots=True)
class GripChangeFormValues:
    grip: str
    color: str
    changed_on: date
    notes: str


TENSION_VALUES = tuple(18.0 + index * 0.5 for index in range(21))
DEFAULT_TENSION = (22.0, 21.0)

GAUGE_VALUES = (1.10, 1.15, 1.20, 1.25, 1.30, 1.35, 1.40)
DEFAULT_GAUGE = 1.25


def _build_gauge_picker(*, initial_value: float) -> tuple[ft.Control, Callable[[], float]]:
    selected_value = initial_value if initial_value in GAUGE_VALUES else DEFAULT_GAUGE

    def select_gauge(
        event: ft.Event[ft.CupertinoPicker],
    ) -> None:
        nonlocal selected_value
        selected_value = GAUGE_VALUES[int(event.data)]

    picker = ft.CupertinoPicker(
        controls=[
            ft.Text(f"{value:.2f}", text_align=ft.TextAlign.CENTER) for value in GAUGE_VALUES
        ],
        selected_index=GAUGE_VALUES.index(selected_value),
        item_extent=36,
        magnification=1.15,
        use_magnifier=True,
        looping=False,
        on_change=select_gauge,
    )

    return (
        ft.Column(
            spacing=4,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Text(
                    "Gauge (mm)",
                    size=13,
                    weight=ft.FontWeight.BOLD,
                ),
                ft.Container(height=120, content=picker),
            ],
        ),
        lambda: selected_value,
    )


def _build_tension_picker(
    *, label: str, initial_value: float
) -> tuple[ft.Control, Callable[[], float]]:
    selected_value = initial_value if initial_value in TENSION_VALUES else DEFAULT_TENSION

    def select_tension(event: ft.Event[ft.CupertinoPicker]) -> None:
        nonlocal selected_value
        selected_value = TENSION_VALUES[int(event.data)]

    picker = ft.CupertinoPicker(
        controls=[
            ft.Text(f"{value:g}", text_align=ft.TextAlign.CENTER) for value in TENSION_VALUES
        ],
        selected_index=TENSION_VALUES.index(selected_value),
        item_extent=36,
        magnification=1.15,
        use_magnifier=True,
        on_change=select_tension,
    )

    return (
        ft.Column(
            expand=True,
            spacing=4,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Text(label, size=13),
                ft.Container(
                    height=120,
                    content=picker,
                ),
            ],
        ),
        lambda: selected_value,
    )


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

    gauge_picker, get_gauge = _build_gauge_picker(
        initial_value=(current.gauge if current is not None else DEFAULT_GAUGE)
    )

    current_mains_tension = current.mains_tension if current is not None else DEFAULT_TENSION[0]
    current_crosses_tension = current.crosses_tension if current is not None else DEFAULT_TENSION[1]

    mains_picker, get_mains_tension = _build_tension_picker(
        label="Mains", initial_value=current_mains_tension
    )
    crosses_picker, get_crosses_tension = _build_tension_picker(
        label="Crosses", initial_value=current_crosses_tension
    )

    tension_picker = ft.Column(
        spacing=4,
        controls=[
            ft.Text("Tension (kg)", size=13, weight=ft.FontWeight.BOLD),
            ft.Row(spacing=12, controls=[mains_picker, crosses_picker]),
        ],
    )

    date_field, get_date = _build_date_field(
        show_dialog=show_dialog,
    )

    notes = _build_notes_field()

    def submit(_: object) -> None:
        string_value = _text(string.value)

        string.error = None

        if not string_value:
            string.error = "String is required"

        if string.error:
            return

        on_submit(
            StringChangeFormValues(
                string=string_value,
                gauge=get_gauge(),
                changed_on=get_date(),
                notes=_text(notes.value),
                mains_tension=get_mains_tension(),
                crosses_tension=get_crosses_tension(),
            )
        )

    return _build_dialog(
        title="Log string change",
        racket_name=racket.name,
        controls=[string, gauge_picker, tension_picker, date_field, notes],
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

    field = ft.TextField(label="Date", value=format_date(selected_date), read_only=True)

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
