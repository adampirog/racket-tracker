from unittest.mock import Mock

from racket_tracker.app import RacketTrackerApp
from racket_tracker.data.models import Racket


def test_refresh_after_write_selects_preferred_racket() -> None:
    repository = Mock()
    repository.get_all.return_value = [
        Racket(id=1, name="One", model="Model"),
        Racket(id=2, name="Two", model="Model"),
        Racket(id=3, name="Three", model="Model"),
    ]

    app = RacketTrackerApp(page=Mock(), repository=repository)
    app.selected_racket_id = 1

    app._render = Mock()
    app._show_message = Mock()

    app._refresh_after_write(preferred_id=3, success_message="Saved")

    assert app.selected_racket_id == 3
