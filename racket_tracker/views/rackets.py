from collections.abc import Callable, Sequence

import flet as ft

from racket_tracker.data.models import Racket
from racket_tracker.formatting import format_date, format_relative_date
from racket_tracker.theme import (
    CARD_RADIUS,
    GRIP_ICON_BG,
    OUTLINE,
    PRIMARY,
    PRIMARY_SOFT,
    RACKET_CARD_BG,
    SECONDARY,
    STRING_ICON_BG,
    SURFACE,
    SURFACE_MUTED,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
)


def build_rackets_view(
    *,
    rackets: Sequence[Racket],
    selected_racket_id: int | None,
    on_select_racket: Callable[[int], None],
    on_add_racket: Callable[[], None],
    on_edit_racket: Callable[[Racket], None],
    on_string_change: Callable[[Racket], None],
    on_grip_change: Callable[[Racket], None],
    on_settings: Callable[[], None],
) -> ft.Control:

    controls: list[ft.Control] = [
        _build_header(on_settings),
        _build_racket_selector(
            rackets=rackets,
            selected_racket_id=selected_racket_id,
            on_select_racket=on_select_racket,
            on_add_racket=on_add_racket,
        ),
    ]

    selected_racket = _find_selected_racket(rackets=rackets, selected_racket_id=selected_racket_id)

    if selected_racket is None:
        controls.append(_build_empty_rackets_state(on_add_racket=on_add_racket))
    else:
        controls.extend(
            [
                _build_racket_card(racket=selected_racket, on_edit=on_edit_racket),
                _build_string_card(selected_racket, on_click=on_string_change),
                _build_grip_card(selected_racket, on_click=on_grip_change),
            ]
        )

    return ft.Column(expand=True, scroll=ft.ScrollMode.AUTO, spacing=16, controls=controls)


def _find_selected_racket(
    *, rackets: Sequence[Racket], selected_racket_id: int | None
) -> Racket | None:
    if selected_racket_id is None:
        return None

    return next((racket for racket in rackets if racket.id == selected_racket_id), None)


def _build_header(on_settings: Callable[[], None]) -> ft.Control:
    return ft.Row(
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            ft.Text("Racket Tracker", size=28, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
            ft.IconButton(
                icon=ft.Icons.SETTINGS_OUTLINED,
                tooltip="Settings",
                on_click=lambda _: on_settings(),
            ),
        ],
    )


def _build_racket_selector(
    *,
    rackets: Sequence[Racket],
    selected_racket_id: int | None,
    on_select_racket: Callable[[int], None],
    on_add_racket: Callable[[], None],
) -> ft.Control:
    controls = [
        _build_racket_chip(
            racket=racket,
            selected=racket.id == selected_racket_id,
            on_select_racket=on_select_racket,
        )
        for racket in rackets
    ]

    controls.append(
        ft.Container(
            bgcolor=SURFACE_MUTED,
            border_radius=12,
            content=ft.IconButton(
                icon=ft.Icons.ADD, tooltip="Add racket", on_click=lambda _: on_add_racket()
            ),
        )
    )

    return ft.Row(controls=controls, spacing=8, scroll=ft.ScrollMode.HIDDEN)


def _build_racket_chip(
    *, racket: Racket, selected: bool, on_select_racket: Callable[[int], None]
) -> ft.Control:
    def handle_select(_: ft.Event[ft.Chip]) -> None:
        if racket.id is not None:
            on_select_racket(racket.id)

    return ft.Chip(
        label=ft.Text(racket.name),
        selected=selected,
        selected_color=PRIMARY_SOFT,
        bgcolor=SURFACE_MUTED,
        show_checkmark=False,
        shape=ft.RoundedRectangleBorder(radius=12),
        on_select=handle_select,
    )


def _build_racket_card(*, racket: Racket, on_edit: Callable[[Racket], None]) -> ft.Control:
    model_label = f"{racket.brand} {racket.model}" if racket.brand else racket.model

    return ft.Container(
        bgcolor=RACKET_CARD_BG,
        border_radius=CARD_RADIUS,
        padding=16,
        content=ft.Row(
            spacing=16,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Container(
                    width=92,
                    height=130,
                    border_radius=14,
                    bgcolor=SURFACE,
                    alignment=ft.Alignment.CENTER,
                    content=ft.Icon(ft.Icons.SPORTS_TENNIS, size=58, color=PRIMARY),
                ),
                ft.Column(
                    expand=True,
                    spacing=5,
                    controls=[
                        ft.Text(
                            racket.name, size=20, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY
                        ),
                        ft.Text(model_label, size=14, color=TEXT_SECONDARY),
                        ft.Container(height=14),
                        ft.Row(
                            alignment=ft.MainAxisAlignment.END,
                            controls=[
                                ft.IconButton(
                                    icon=ft.Icons.EDIT_OUTLINED,
                                    tooltip="Edit racket",
                                    on_click=lambda _: on_edit(racket),
                                ),
                            ],
                        ),
                    ],
                ),
            ],
        ),
    )


def _build_string_card(racket: Racket, *, on_click: Callable[[Racket], None]) -> ft.Control:
    change = racket.current_string

    if change is None:
        return _build_empty_equipment_card(
            title="Strings",
            message="No string recorded yet",
            icon=ft.Icons.REPEAT,
            icon_bg=STRING_ICON_BG,
            icon_color=PRIMARY,
            on_click=lambda: on_click(racket),
        )

    value = change.string

    if change.gauge:
        value = f"{value} {change.gauge}"

    return _build_equipment_card(
        title="Strings",
        value=value,
        action_label="Restrung",
        date=format_date(change.changed_on),
        relative_date=format_relative_date(change.changed_on),
        icon=ft.Icons.REPEAT,
        icon_bg=STRING_ICON_BG,
        icon_color=PRIMARY,
        on_click=lambda: on_click(racket),
    )


def _build_grip_card(racket: Racket, *, on_click: Callable[[Racket], None]) -> ft.Control:
    change = racket.current_grip

    if change is None:
        return _build_empty_equipment_card(
            title="Grip",
            message="No grip recorded yet",
            icon=ft.Icons.BACK_HAND_OUTLINED,
            icon_bg=GRIP_ICON_BG,
            icon_color=SECONDARY,
            on_click=lambda: on_click(racket),
        )

    value = change.grip

    if change.color:
        value = f"{value} ({change.color})"

    return _build_equipment_card(
        title="Grip",
        value=value,
        action_label="Regripped",
        date=format_date(change.changed_on),
        relative_date=format_relative_date(change.changed_on),
        icon=ft.Icons.BACK_HAND_OUTLINED,
        icon_bg=GRIP_ICON_BG,
        icon_color=SECONDARY,
        on_click=lambda: on_click(racket),
    )


def _build_equipment_card(
    *,
    title: str,
    value: str,
    action_label: str,
    date: str,
    relative_date: str,
    icon: ft.IconData,
    icon_bg: str,
    icon_color: str,
    on_click: Callable[[], None],
) -> ft.Control:
    return ft.Container(
        bgcolor=SURFACE,
        border_radius=CARD_RADIUS,
        border=ft.Border.all(1, OUTLINE),
        ink=True,
        on_click=lambda _: on_click(),
        padding=14,
        content=ft.Row(
            spacing=14,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                _build_equipment_icon(
                    icon=icon,
                    background=icon_bg,
                    color=icon_color,
                ),
                ft.Column(
                    expand=True,
                    spacing=3,
                    controls=[
                        ft.Text(title, size=15, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                        ft.Text(value, size=14, color=TEXT_PRIMARY),
                        ft.Container(height=4),
                        ft.Text(action_label, size=12, color=TEXT_SECONDARY),
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            controls=[
                                ft.Text(date, size=13, color=TEXT_PRIMARY),
                                ft.Text(relative_date, size=12, color=TEXT_SECONDARY),
                            ],
                        ),
                    ],
                ),
                ft.Icon(ft.Icons.CHEVRON_RIGHT, color=TEXT_SECONDARY, size=20),
            ],
        ),
    )


def _build_empty_equipment_card(
    *,
    title: str,
    message: str,
    icon: ft.IconData,
    icon_bg: str,
    icon_color: str,
    on_click: Callable[[], None],
) -> ft.Control:
    return ft.Container(
        bgcolor=SURFACE,
        border_radius=CARD_RADIUS,
        border=ft.Border.all(1, OUTLINE),
        padding=14,
        ink=True,
        on_click=lambda _: on_click(),
        content=ft.Row(
            spacing=14,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                _build_equipment_icon(
                    icon=icon,
                    background=icon_bg,
                    color=icon_color,
                ),
                ft.Column(
                    expand=True,
                    spacing=3,
                    controls=[
                        ft.Text(title, size=15, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                        ft.Text(message, size=14, color=TEXT_SECONDARY),
                    ],
                ),
                ft.Icon(ft.Icons.CHEVRON_RIGHT, color=TEXT_SECONDARY, size=20),
            ],
        ),
    )


def _build_equipment_icon(*, icon: ft.IconData, background: str, color: str) -> ft.Control:
    return ft.Container(
        width=44,
        height=44,
        border_radius=22,
        bgcolor=background,
        alignment=ft.Alignment.CENTER,
        content=ft.Icon(icon, color=color, size=23),
    )


def _build_empty_rackets_state(*, on_add_racket: Callable[[], None]) -> ft.Control:
    return ft.Container(
        expand=True,
        alignment=ft.Alignment.CENTER,
        padding=32,
        content=ft.Column(
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=12,
            controls=[
                ft.Container(
                    width=76,
                    height=76,
                    border_radius=38,
                    bgcolor=PRIMARY_SOFT,
                    alignment=ft.Alignment.CENTER,
                    content=ft.Icon(ft.Icons.SPORTS_TENNIS, size=38, color=PRIMARY),
                ),
                ft.Text("No rackets yet", size=20, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                ft.Text(
                    "Add your first racket to start tracking strings and grips.",
                    size=14,
                    color=TEXT_SECONDARY,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Container(height=4),
                ft.Button(
                    content="Add racket", icon=ft.Icons.ADD, on_click=lambda _: on_add_racket()
                ),
            ],
        ),
    )
