from collections.abc import Callable
from dataclasses import dataclass

import flet as ft

from racket_tracker.data.models import Racket


@dataclass(frozen=True, slots=True)
class RacketFormValues:
    name: str
    brand: str
    model: str
    notes: str


def build_racket_dialog(
    *,
    on_submit: Callable[[RacketFormValues], None],
    on_cancel: Callable[[], None],
    racket: Racket | None = None,
    on_delete: Callable[[], None] | None = None,
) -> ft.AlertDialog:
    editing = racket is not None

    name = ft.TextField(
        label="Name",
        hint_text="e.g. Match racket",
        value=racket.name if racket else "",
        autofocus=True,
        max_length=100,
        capitalization=ft.TextCapitalization.SENTENCES,
    )

    brand = ft.TextField(
        label="Brand",
        hint_text="e.g. Babolat",
        value=racket.brand if racket else "",
        max_length=100,
        capitalization=ft.TextCapitalization.WORDS,
        autocorrect=False,
    )

    model = ft.TextField(
        label="Model",
        hint_text="e.g. Pure Drive (2021)",
        value=racket.model if racket else "",
        max_length=100,
        capitalization=ft.TextCapitalization.WORDS,
        autocorrect=False,
    )

    notes = ft.TextField(
        label="Notes",
        hint_text="Optional",
        value=racket.notes if racket else "",
        multiline=True,
        min_lines=2,
        max_lines=4,
        capitalization=ft.TextCapitalization.SENTENCES,
    )

    def submit(_: object) -> None:
        name_value = (name.value or "").strip()
        model_value = (model.value or "").strip()

        name.error = None
        model.error = None

        if not name_value:
            name.error = "Name is required"

        if not model_value:
            model.error = "Model is required"

        if name.error or model.error:
            return

        on_submit(
            RacketFormValues(
                name=name_value,
                brand=_text(brand.value),
                model=model_value,
                notes=_text(notes.value),
            )
        )

    actions: list[ft.Control] = []

    if on_delete is not None:
        actions.append(ft.TextButton(content="Delete", on_click=lambda _: on_delete()))

    actions.extend(
        [
            ft.TextButton(content="Cancel", on_click=lambda _: on_cancel()),
            ft.Button(content="Save" if editing else "Add racket", on_click=submit),
        ]
    )

    return ft.AlertDialog(
        modal=True,
        scrollable=True,
        title=ft.Text("Edit racket" if editing else "Add racket"),
        content=ft.Column(
            spacing=12,
            controls=[name, brand, model, notes],
        ),
        actions=actions,
        actions_alignment=ft.MainAxisAlignment.END,
    )


def build_delete_racket_dialog(
    *, racket: Racket, on_confirm: Callable[[], None], on_cancel: Callable[[], None]
) -> ft.AlertDialog:
    return ft.AlertDialog(
        modal=True,
        title=ft.Text("Delete racket?"),
        content=ft.Text(
            f'"{racket.name}" and all of its string and grip history will be permanently deleted.'
        ),
        actions=[
            ft.TextButton(
                content="Cancel",
                on_click=lambda _: on_cancel(),
            ),
            ft.Button(
                content="Delete",
                on_click=lambda _: on_confirm(),
            ),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )


def _text(value: str | None) -> str:
    return (value or "").strip()
