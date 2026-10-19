from datetime import date

import flet as ft

from racket_tracker.data.models import Racket, StringChange
from racket_tracker.views.history import build_history_view


def test_history_view_builds_when_empty() -> None:
    view = build_history_view(rackets=[], on_delete=lambda _kind, _record_id: None)

    assert isinstance(view, ft.Control)


def test_history_view_builds_with_history() -> None:
    racket = Racket(id=1, name="Match racket", model="Pure Drive")
    racket.string_changes.append(
        StringChange(racket_id=1, string="RPM Blast", gauge="1.25", changed_on=date(2026, 10, 15))
    )

    view = build_history_view(rackets=[racket], on_delete=lambda _kind, _record_id: None)

    assert isinstance(view, ft.Control)
