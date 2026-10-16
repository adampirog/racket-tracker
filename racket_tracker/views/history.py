from dataclasses import dataclass
from datetime import date
from typing import Literal

import flet as ft

from racket_tracker.data.models import Racket
from racket_tracker.formatting import format_date, format_gauge
from racket_tracker.theme import (
    CARD_RADIUS,
    GRIP_ICON_BG,
    OUTLINE,
    PRIMARY,
    SECONDARY,
    STRING_ICON_BG,
    SURFACE,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
)


HistoryKind = Literal["string", "grip"]


@dataclass(frozen=True, slots=True)
class HistoryEntry:
    kind: HistoryKind
    changed_on: date
    racket_name: str
    value: str
    notes: str


def build_history_view(*, rackets: list[Racket]):
    entries = _build_history_entries(rackets)

    if not entries:
        return _build_empty_history()


def _build_history_entries(rackets: list[Racket]) -> list[HistoryEntry]:
    entries: list[HistoryEntry] = []

    for racket in rackets:
        for change in racket.string_changes:
            value = change.string

            if change.gauge:
                value = f"{value} {format_gauge(change.gauge)}"

            entries.append(
                HistoryEntry(
                    kind="string",
                    changed_on=change.changed_on,
                    racket_name=racket.name,
                    value=value,
                    notes=change.notes,
                )
            )

        for change in racket.grip_changes:
            value = change.grip

            if change.color:
                value = f"{value} ({change.color})"

            entries.append(
                HistoryEntry(
                    kind="grip",
                    changed_on=change.changed_on,
                    racket_name=racket.name,
                    value=value,
                    notes=change.notes,
                )
            )

    return sorted(entries, key=lambda entry: entry.changed_on, reverse=True)


def _build_history_card(entry: HistoryEntry) -> ft.Control:
    if entry.kind == "string":
        title = "Restrung"
        icon = ft.Icons.REPEAT
        icon_bg = STRING_ICON_BG
        icon_color = PRIMARY
    else:
        title = "Regripped"
        icon = ft.Icons.BACK_HAND_OUTLINED
        icon_bg = GRIP_ICON_BG
        icon_color = SECONDARY

    details: list[ft.Control] = [
        ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Text(title, size=14, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                ft.Text(format_date(entry.changed_on), size=12, color=TEXT_SECONDARY),
            ],
        ),
        ft.Text(entry.value, size=14, color=TEXT_PRIMARY),
        ft.Text(entry.racket_name, size=12, color=TEXT_SECONDARY),
    ]

    if entry.notes:
        details.extend(
            [
                ft.Divider(height=12, color=OUTLINE),
                ft.Text(entry.notes, size=12, color=TEXT_SECONDARY),
            ]
        )

    return ft.Container(
        bgcolor=SURFACE,
        border=ft.Border.all(1, OUTLINE),
        border_radius=CARD_RADIUS,
        padding=14,
        content=ft.Row(
            spacing=14,
            vertical_alignment=ft.CrossAxisAlignment.START,
            controls=[
                ft.Container(
                    width=42,
                    height=42,
                    border_radius=21,
                    bgcolor=icon_bg,
                    alignment=ft.Alignment.CENTER,
                    content=ft.Icon(icon, size=22, color=icon_color),
                ),
                ft.Column(expand=True, spacing=4, controls=details),
            ],
        ),
    )


def _build_empty_history() -> ft.Control:
    return ft.Column(
        expand=True,
        controls=[
            ft.Text("History", size=28, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
            ft.Container(
                expand=True,
                alignment=ft.Alignment.CENTER,
                content=ft.Column(
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=12,
                    controls=[
                        ft.Icon(ft.Icons.HISTORY, size=48, color=PRIMARY),
                        ft.Text(
                            "No history yet", size=20, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY
                        ),
                        ft.Text(
                            "String and grip changes will appear here after you log them.",
                            size=14,
                            color=TEXT_SECONDARY,
                            text_align=ft.TextAlign.CENTER,
                        ),
                    ],
                ),
            ),
        ],
    )
