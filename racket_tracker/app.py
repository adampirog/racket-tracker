import flet as ft

from racket_tracker.data.models import GripChange, Racket, StringChange
from racket_tracker.data.repository import RacketRepository
from racket_tracker.theme import (
    BACKGROUND,
    PAGE_PADDING,
    PRIMARY,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
    build_theme,
)
from racket_tracker.views.maintenance_form import (
    GripChangeFormValues,
    StringChangeFormValues,
    build_grip_change_dialog,
    build_string_change_dialog,
)
from racket_tracker.views.racket_form import (
    RacketFormValues,
    build_delete_racket_dialog,
    build_racket_dialog,
)
from racket_tracker.views.rackets import build_rackets_view


class RacketTrackerApp:
    def __init__(
        self,
        *,
        page: ft.Page,
        repository: RacketRepository,
    ) -> None:
        self.page = page
        self.repository = repository

        self.rackets: list[Racket] = []
        self.selected_racket_id: int | None = None
        self.selected_tab = 0

        self.body = ft.Container(
            expand=True,
            padding=PAGE_PADDING,
        )

    def mount(self) -> None:
        self._configure_page()
        self._reload_rackets()

        self.page.navigation_bar = self._build_navigation_bar()

        self._render()

        self.page.add(ft.SafeArea(expand=True, content=self.body))

    def _configure_page(self) -> None:
        self.page.title = "Racket Tracker"
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.theme = build_theme()
        self.page.bgcolor = BACKGROUND
        self.page.padding = 0

    def _reload_rackets(self, *, preferred_id: int | None = None) -> None:
        self.rackets = self.repository.get_all()
        racket_ids = {racket.id for racket in self.rackets}

        if preferred_id in racket_ids:
            self.selected_racket_id = preferred_id
        elif self.selected_racket_id not in racket_ids:
            self.selected_racket_id = self.rackets[0].id if self.rackets else None

    def _select_racket(self, racket_id: int) -> None:
        self.selected_racket_id = racket_id
        self._render()

    def _select_tab(self, event: ft.Event[ft.NavigationBar]) -> None:
        if event.control.selected_index is None:
            return

        self.selected_tab = event.control.selected_index
        self._render()

    # ------------------------------------------------------------------
    # Racket CRUD
    # ------------------------------------------------------------------

    def _show_add_racket(self) -> None:
        self.page.show_dialog(
            build_racket_dialog(on_submit=self._add_racket, on_cancel=self._close_dialog)
        )

    def _add_racket(self, values: RacketFormValues) -> None:
        racket = self.repository.add(
            Racket(
                name=values.name,
                brand=values.brand,
                model=values.model,
                notes=values.notes,
            )
        )

        self.page.pop_dialog()

        self._reload_rackets(
            preferred_id=racket.id,
        )
        self._render()

    def _show_edit_racket(self, racket: Racket) -> None:
        self.page.show_dialog(
            build_racket_dialog(
                racket=racket,
                on_submit=lambda values: self._update_racket(
                    racket.id,
                    values,
                ),
                on_delete=lambda: self._show_delete_confirmation(racket),
                on_cancel=self._close_dialog,
            )
        )

    def _update_racket(self, racket_id: int, values: RacketFormValues) -> None:
        self.repository.update(
            racket_id,
            name=values.name,
            brand=values.brand,
            model=values.model,
            notes=values.notes,
        )

        self.page.pop_dialog()

        self._reload_rackets(
            preferred_id=racket_id,
        )
        self._render()

    def _show_delete_confirmation(self, racket: Racket) -> None:
        self.page.pop_dialog()

        self.page.show_dialog(
            build_delete_racket_dialog(
                racket=racket,
                on_confirm=lambda: self._delete_racket(racket.id),
                on_cancel=self._close_dialog,
            )
        )

    def _delete_racket(self, racket_id: int) -> None:
        replacement_id = self._replacement_after_delete(racket_id)

        self.repository.delete(racket_id)
        self.page.pop_dialog()

        self._reload_rackets(
            preferred_id=replacement_id,
        )
        self._render()

    def _replacement_after_delete(self, racket_id: int) -> int | None:
        ids = [racket.id for racket in self.rackets if racket.id is not None]

        if racket_id not in ids:
            return None

        index = ids.index(racket_id)
        remaining = ids[:index] + ids[index + 1 :]

        if not remaining:
            return None

        return remaining[min(index, len(remaining) - 1)]

    # ------------------------------------------------------------------
    # Rendering
    # ------------------------------------------------------------------

    def _render(self) -> None:
        if self.selected_tab == 0:
            self._render_rackets()
        elif self.selected_tab == 1:
            self._render_placeholder(
                title="History",
                message="Your string and grip changes will appear here.",
                icon=ft.Icons.HISTORY,
            )
        else:
            self._render_placeholder(
                title="Summary",
                message="Statistics and equipment insights will live here.",
                icon=ft.Icons.BAR_CHART,
            )

    def _render_rackets(self) -> None:
        self.body.content = build_rackets_view(
            rackets=self.rackets,
            selected_racket_id=self.selected_racket_id,
            on_select_racket=self._select_racket,
            on_add_racket=self._show_add_racket,
            on_edit_racket=self._show_edit_racket,
            on_string_change=self._show_string_change,
            on_grip_change=self._show_grip_change,
            on_settings=lambda: self._show_message("Settings will come later."),
        )

        self.page.floating_action_button = ft.FloatingActionButton(
            icon=ft.Icons.ADD,
            bgcolor=PRIMARY,
            tooltip="Add racket",
            on_click=lambda _: self._show_add_racket(),
        )

    def _render_placeholder(
        self,
        *,
        title: str,
        message: str,
        icon: ft.IconData,
    ) -> None:
        self.body.content = ft.Column(
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

        self.page.floating_action_button = None

    def _build_navigation_bar(self) -> ft.NavigationBar:
        return ft.NavigationBar(
            selected_index=self.selected_tab,
            on_change=self._select_tab,
            destinations=[
                ft.NavigationBarDestination(
                    label="Rackets",
                    icon=ft.Icons.SPORTS_TENNIS,
                    selected_icon=ft.Icons.SPORTS_TENNIS,
                ),
                ft.NavigationBarDestination(
                    label="History",
                    icon=ft.Icons.HISTORY_OUTLINED,
                    selected_icon=ft.Icons.HISTORY,
                ),
                ft.NavigationBarDestination(
                    label="Summary",
                    icon=ft.Icons.BAR_CHART_OUTLINED,
                    selected_icon=ft.Icons.BAR_CHART,
                ),
            ],
        )

    def _show_message(self, message: str) -> None:
        self.page.show_dialog(ft.SnackBar(content=ft.Text(message)))

    # ------------------------------------------------------------------
    # Maintenance logging
    # ------------------------------------------------------------------

    def _show_string_change(self, racket: Racket) -> None:
        self.page.show_dialog(
            build_string_change_dialog(
                racket_name=racket.name,
                show_dialog=self.page.show_dialog,
                on_submit=lambda values: self._add_string_change(
                    racket.id,
                    values,
                ),
                on_cancel=self._close_dialog,
            )
        )

    def _add_string_change(self, racket_id: int, values: StringChangeFormValues) -> None:
        self.repository.add_string_change(
            StringChange(
                racket_id=racket_id,
                string=values.string,
                gauge=values.gauge,
                changed_on=values.changed_on,
                notes=values.notes,
            )
        )

        self.page.pop_dialog()

        self._reload_rackets(
            preferred_id=racket_id,
        )
        self._render()

    def _show_grip_change(self, racket: Racket) -> None:
        self.page.show_dialog(
            build_grip_change_dialog(
                racket_name=racket.name,
                show_dialog=self.page.show_dialog,
                on_submit=lambda values: self._add_grip_change(
                    racket.id,
                    values,
                ),
                on_cancel=self._close_dialog,
            )
        )

    def _add_grip_change(self, racket_id: int, values: GripChangeFormValues) -> None:
        self.repository.add_grip_change(
            GripChange(
                racket_id=racket_id,
                grip=values.grip,
                color=values.color,
                changed_on=values.changed_on,
                notes=values.notes,
            )
        )

        self.page.pop_dialog()

        self._reload_rackets(
            preferred_id=racket_id,
        )
        self._render()

    def _close_dialog(self) -> None:
        self.page.pop_dialog()
