from collections.abc import Callable, Sequence

import flet as ft

from racket_tracker.models import Racket
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
    rackets: Sequence[Racket],
    selected_racket_id: int,
    on_select_racket: Callable[[int], None],
    on_add_racket: Callable[[], None],
    on_edit_racket: Callable[[], None],
    on_settings: Callable[[], None],
) -> ft.Control:
    selected_racket = next(racket for racket in rackets if racket.id == selected_racket_id)

    return ft.Column(
        expand=True,
        scroll=ft.ScrollMode.AUTO,
        spacing=16,
        controls=[
            _build_header(on_settings),
            _build_racket_selector(
                rackets=rackets,
                selected_racket_id=selected_racket_id,
                on_select_racket=on_select_racket,
                on_add_racket=on_add_racket,
            ),
            _build_racket_card(
                racket=selected_racket,
                on_edit=on_edit_racket,
            ),
            _build_equipment_card(
                title="Strings",
                value="Babolat RPM Blast 1.25",
                action_label="Restrung",
                date="12 Jun 2025",
                relative_date="3 weeks ago",
                icon=ft.Icons.REPEAT,
                icon_bg=STRING_ICON_BG,
                icon_color=PRIMARY,
            ),
            _build_equipment_card(
                title="Grip",
                value="Wilson Pro Overgrip (White)",
                action_label="Regripped",
                date="20 May 2025",
                relative_date="1 month ago",
                icon=ft.Icons.BACK_HAND_OUTLINED,
                icon_bg=GRIP_ICON_BG,
                icon_color=SECONDARY,
            ),
        ],
    )


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
    rackets: Sequence[Racket],
    selected_racket_id: int,
    on_select_racket: Callable[[int], None],
    on_add_racket: Callable[[], None],
) -> ft.Control:
    racket_chips: list[ft.Control] = []

    for racket in rackets:

        def handle_select(
            _: ft.Event[ft.Chip],
            racket_id: int = racket.id,
        ) -> None:
            on_select_racket(racket_id)

        racket_chips.append(
            ft.Chip(
                label=ft.Text(racket.name),
                selected=racket.id == selected_racket_id,
                selected_color=PRIMARY_SOFT,
                bgcolor=SURFACE_MUTED,
                show_checkmark=False,
                shape=ft.RoundedRectangleBorder(radius=12),
                on_select=handle_select,
            )
        )

    racket_chips.append(
        ft.Container(
            bgcolor=SURFACE_MUTED,
            border_radius=12,
            content=ft.IconButton(
                icon=ft.Icons.ADD,
                tooltip="Add racket",
                on_click=lambda _: on_add_racket(),
            ),
        )
    )

    return ft.Row(controls=racket_chips, spacing=8, scroll=ft.ScrollMode.HIDDEN)


def _build_racket_card(racket: Racket, on_edit: Callable[[], None]) -> ft.Control:
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
                                    on_click=lambda _: on_edit(),
                                ),
                            ],
                        ),
                    ],
                ),
            ],
        ),
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
) -> ft.Control:
    return ft.Container(
        bgcolor=SURFACE,
        border_radius=CARD_RADIUS,
        border=ft.Border.all(1, OUTLINE),
        padding=14,
        content=ft.Row(
            spacing=14,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Container(
                    width=44,
                    height=44,
                    border_radius=22,
                    bgcolor=icon_bg,
                    alignment=ft.Alignment.CENTER,
                    content=ft.Icon(icon, color=icon_color, size=23),
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
