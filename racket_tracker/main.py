import flet as ft

from racket_tracker.models import Racket
from racket_tracker.theme import (
    BACKGROUND,
    PAGE_PADDING,
    PRIMARY,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
    build_theme,
)
from racket_tracker.views.rackets import build_rackets_view


def main(page: ft.Page) -> None:
    page.title = "Racket Tracker"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.theme = build_theme()
    page.bgcolor = BACKGROUND
    page.padding = 0

    rackets = [
        Racket(id=1, name="Pure Drive #1", brand="Babolat", model="Pure Drive (2021)"),
        Racket(id=2, name="Pure Drive #2", brand="Babolat", model="Pure Drive (2021)"),
        Racket(id=3, name="Radical", brand="Head", model="Radical MP (2023)"),
    ]

    selected_tab = 0
    selected_racket_id = rackets[0].id

    body = ft.Container(
        expand=True,
        padding=PAGE_PADDING,
    )

    def show_not_implemented(message: str) -> None:
        page.show_dialog(ft.SnackBar(ft.Text(message)))

    def select_racket(racket_id: int) -> None:
        nonlocal selected_racket_id

        selected_racket_id = racket_id
        render()

    def select_tab(e: ft.Event[ft.NavigationBar]) -> None:
        nonlocal selected_tab

        if e.control.selected_index is None:
            return

        selected_tab = e.control.selected_index
        render()

    def build_placeholder(
        title: str,
        message: str,
        icon: ft.IconData,
    ) -> ft.Control:
        return ft.Column(
            expand=True,
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=12,
            controls=[
                ft.Icon(icon, size=48, color=PRIMARY),
                ft.Text(title, size=24, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                ft.Text(message, size=14, color=TEXT_SECONDARY, text_align=ft.TextAlign.CENTER),
            ],
        )

    def render() -> None:
        if selected_tab == 0:
            body.content = build_rackets_view(
                rackets=rackets,
                selected_racket_id=selected_racket_id,
                on_select_racket=select_racket,
                on_add_racket=lambda: show_not_implemented("Adding rackets comes next."),
                on_edit_racket=lambda: show_not_implemented("Editing rackets comes next."),
                on_settings=lambda: show_not_implemented("Settings will come later."),
            )

            page.floating_action_button = ft.FloatingActionButton(
                icon=ft.Icons.ADD,
                bgcolor=PRIMARY,
                tooltip="Add racket",
                on_click=lambda _: show_not_implemented("Adding rackets comes next."),
            )

        elif selected_tab == 1:
            body.content = build_placeholder(
                title="History",
                message="Your string and grip changes will appear here.",
                icon=ft.Icons.HISTORY,
            )
            page.floating_action_button = None

        else:
            body.content = build_placeholder(
                title="Summary",
                message="Statistics and equipment insights will live here.",
                icon=ft.Icons.BAR_CHART,
            )
            page.floating_action_button = None

    page.navigation_bar = ft.NavigationBar(
        selected_index=selected_tab,
        on_change=select_tab,
        destinations=[
            ft.NavigationBarDestination(
                label="Rackets", icon=ft.Icons.SPORTS_TENNIS, selected_icon=ft.Icons.SPORTS_TENNIS
            ),
            ft.NavigationBarDestination(
                label="History", icon=ft.Icons.HISTORY_OUTLINED, selected_icon=ft.Icons.HISTORY
            ),
            ft.NavigationBarDestination(
                label="Summary", icon=ft.Icons.BAR_CHART_OUTLINED, selected_icon=ft.Icons.BAR_CHART
            ),
        ],
    )

    render()

    page.add(ft.SafeArea(expand=True, content=body))


if __name__ == "__main__":
    ft.run(main)
