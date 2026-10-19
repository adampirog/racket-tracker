import logging

import flet as ft
from sqlalchemy.exc import SQLAlchemyError

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
from racket_tracker.views.history import (
    HistoryKind,
    build_delete_history_dialog,
    build_history_view,
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


logger = logging.getLogger(__name__)


class RacketTrackerApp:
    def __init__(self, *, page: ft.Page, repository: RacketRepository) -> None:
        self.page = page
        self.repository = repository

        self.rackets: list[Racket] = []
        self.selected_racket_id: int | None = None
        self.selected_tab = 0

        self.navigation_bar: ft.NavigationBar | None = None

        self.body = ft.Container(expand=True, padding=PAGE_PADDING)

    def mount(self) -> None:
        self._configure_page()

        load_failed = False

        try:
            self._reload_rackets()
        except SQLAlchemyError:
            logger.exception("Failed to load rackets")
            self.rackets = []
            self.selected_racket_id = None
            load_failed = True

        self.navigation_bar = self._build_navigation_bar()
        self.page.navigation_bar = self.navigation_bar

        self._render()

        self.page.add(ft.SafeArea(expand=True, content=self.body))

        if load_failed:
            self._show_message("Couldn't load your rackets. Please restart the app.")

    def _configure_page(self) -> None:
        self.page.title = "Racket Tracker"
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.theme = build_theme()
        self.page.bgcolor = BACKGROUND
        self.page.padding = 0

    def _reload_rackets(self) -> None:
        selected_id = self.selected_racket_id

        self.rackets = self.repository.get_all()
        racket_ids = {racket.id for racket in self.rackets}

        if selected_id not in racket_ids:
            self.selected_racket_id = self.rackets[0].id if self.rackets else None

    def _refresh_after_write(self, *, preferred_id: int | None, success_message: str) -> None:
        try:
            self._reload_rackets()
        except SQLAlchemyError:
            logger.exception("Failed to reload rackets after write")
            self._show_message("Saved, but couldn't refresh the app. Please restart it.")
            return

        if preferred_id is not None and any(racket.id == preferred_id for racket in self.rackets):
            self.selected_racket_id = preferred_id

        self._render()
        self._show_message(success_message)

    def _select_racket(self, racket_id: int) -> None:
        self.selected_racket_id = racket_id
        self._render()

    def _select_tab(self, event: ft.Event[ft.NavigationBar]) -> None:
        if event.control.selected_index is None:
            return

        self._set_tab(event.control.selected_index)

    def _set_tab(self, index: int) -> None:
        self.selected_tab = index

        if self.navigation_bar is not None:
            self.navigation_bar.selected_index = index

        self._render()
        self.page.update()

    # ------------------------------------------------------------------
    # Racket CRUD
    # ------------------------------------------------------------------

    def _show_add_racket(self) -> None:
        self.page.show_dialog(
            build_racket_dialog(on_submit=self._add_racket, on_cancel=self._close_dialog)
        )

    def _add_racket(self, values: RacketFormValues) -> None:
        try:
            racket = self.repository.add(
                Racket(
                    name=values.name,
                    brand=values.brand,
                    model=values.model,
                    image_id=values.image_id,
                    notes=values.notes,
                )
            )
        except SQLAlchemyError:
            logger.exception("Failed to add racket")
            self._show_message("Couldn't add racket. Please try again.")
            return

        self._close_dialog()

        self._refresh_after_write(preferred_id=racket.id, success_message="Racket added.")

    def _show_edit_racket(self, racket: Racket) -> None:
        self.page.show_dialog(
            build_racket_dialog(
                racket=racket,
                on_submit=lambda values: self._update_racket(racket.id, values),
                on_delete=lambda: self._show_delete_confirmation(racket),
                on_cancel=self._close_dialog,
            )
        )

    def _update_racket(self, racket_id: int, values: RacketFormValues) -> None:
        try:
            self.repository.update(
                racket_id,
                name=values.name,
                brand=values.brand,
                model=values.model,
                image_id=values.image_id,
                notes=values.notes,
            )
        except (SQLAlchemyError, LookupError):
            logger.exception(
                "Failed to update racket %s",
                racket_id,
            )
            self._show_message("Couldn't update racket. Please try again.")
            return

        self._close_dialog()

        self._refresh_after_write(preferred_id=racket_id, success_message="Racket updated.")

    def _show_delete_confirmation(self, racket: Racket) -> None:
        self._close_dialog()

        self.page.show_dialog(
            build_delete_racket_dialog(
                racket=racket,
                on_confirm=lambda: self._delete_racket(racket.id),
                on_cancel=self._close_dialog,
            )
        )

    def _delete_racket(self, racket_id: int) -> None:
        replacement_id = self._replacement_after_delete(racket_id)

        try:
            self.repository.delete(racket_id)
        except SQLAlchemyError:
            logger.exception("Failed to delete racket %s", racket_id)
            self._show_message("Couldn't delete racket. Please try again.")
            return

        self._close_dialog()

        self._refresh_after_write(preferred_id=replacement_id, success_message="Racket deleted.")

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
    # Maintenance logging
    # ------------------------------------------------------------------

    def _show_string_change(self, racket: Racket) -> None:
        self.page.show_dialog(
            build_string_change_dialog(
                racket=racket,
                show_dialog=self.page.show_dialog,
                on_submit=lambda values: self._add_string_change(racket.id, values),
                on_cancel=self._close_dialog,
            )
        )

    def _add_string_change(self, racket_id: int, values: StringChangeFormValues) -> None:
        try:
            self.repository.add_string_change(
                StringChange(
                    racket_id=racket_id,
                    string=values.string,
                    gauge=values.gauge,
                    changed_on=values.changed_on,
                    notes=values.notes,
                )
            )
        except SQLAlchemyError:
            logger.exception("Failed to save string change for racket %s", racket_id)
            self._show_message("Couldn't save string change. Please try again.")
            return

        self._close_dialog()

        self._refresh_after_write(preferred_id=racket_id, success_message="String change saved.")

    def _show_grip_change(self, racket: Racket) -> None:
        self.page.show_dialog(
            build_grip_change_dialog(
                racket=racket,
                show_dialog=self.page.show_dialog,
                on_submit=lambda values: self._add_grip_change(racket.id, values),
                on_cancel=self._close_dialog,
            )
        )

    def _add_grip_change(self, racket_id: int, values: GripChangeFormValues) -> None:
        try:
            self.repository.add_grip_change(
                GripChange(
                    racket_id=racket_id,
                    grip=values.grip,
                    color=values.color,
                    changed_on=values.changed_on,
                    notes=values.notes,
                )
            )
        except SQLAlchemyError:
            logger.exception("Failed to save grip change for racket %s", racket_id)
            self._show_message("Couldn't save grip change. Please try again.")
            return

        self._close_dialog()

        self._refresh_after_write(preferred_id=racket_id, success_message="Grip change saved.")

    def _show_delete_history_entry(self, kind: HistoryKind, record_id: int) -> None:
        self.page.show_dialog(
            build_delete_history_dialog(
                kind=kind,
                on_confirm=lambda: self._delete_history_entry(kind, record_id),
                on_cancel=self._close_dialog,
            )
        )

    def _delete_history_entry(self, kind: HistoryKind, record_id: int) -> None:
        try:
            if kind == "string":
                self.repository.delete_string_change(record_id)
            else:
                self.repository.delete_grip_change(record_id)

        except (SQLAlchemyError, LookupError):
            logger.exception("Failed to delete %s history entry %s", kind, record_id)
            self._show_message("Couldn't delete history entry. Please try again.")
            return

        self._close_dialog()

        self._refresh_after_write(
            preferred_id=self.selected_racket_id, success_message="History entry deleted."
        )

    # ------------------------------------------------------------------
    # Rendering
    # ------------------------------------------------------------------

    def _render(self) -> None:
        if self.selected_tab == 0:
            self._render_rackets()
        elif self.selected_tab == 1:
            self._render_history()
        else:
            self._render_placeholder(
                title="Summary",
                message=("Statistics and equipment insights will live here."),
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

    def _render_history(self) -> None:
        self.body.content = build_history_view(
            rackets=self.rackets, on_delete=self._show_delete_history_entry
        )
        self.page.floating_action_button = None

    def _render_placeholder(self, *, title: str, message: str, icon: ft.IconData) -> None:
        self.body.content = ft.Container(
            expand=True,
            alignment=ft.Alignment.CENTER,
            content=ft.Column(
                tight=True,
                horizontal_alignment=(ft.CrossAxisAlignment.CENTER),
                spacing=12,
                controls=[
                    ft.Icon(icon, size=48, color=PRIMARY),
                    ft.Text(title, size=24, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                    ft.Text(message, size=14, color=TEXT_SECONDARY, text_align=ft.TextAlign.CENTER),
                ],
            ),
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

    # ------------------------------------------------------------------
    # Dialogs / messages
    # ------------------------------------------------------------------

    def _show_message(self, message: str) -> None:
        self.page.show_dialog(ft.SnackBar(content=ft.Text(message)))

    def _close_dialog(self) -> None:
        self.page.pop_dialog()
