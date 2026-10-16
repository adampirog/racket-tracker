from collections.abc import Callable
from dataclasses import dataclass

import flet as ft

from racket_tracker.data.models import Racket
from racket_tracker.racket_images import (
    DEFAULT_RACKET_IMAGE_ID,
    RACKET_IMAGES,
)
from racket_tracker.theme import (
    OUTLINE,
    PRIMARY,
    PRIMARY_SOFT,
    SURFACE,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
)
from racket_tracker.views.racket_image import build_racket_image


@dataclass(frozen=True, slots=True)
class RacketFormValues:
    name: str
    brand: str
    model: str
    image_id: str
    notes: str


def build_racket_dialog(
    *,
    on_submit: Callable[[RacketFormValues], None],
    on_cancel: Callable[[], None],
    racket: Racket | None = None,
    on_delete: Callable[[], None] | None = None,
) -> ft.AlertDialog:
    editing = racket is not None

    image_picker, get_image_id = _build_image_picker(
        initial_image_id=_initial_image_id(racket),
    )

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
        name_value = _text(name.value)
        model_value = _text(model.value)

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
                image_id=get_image_id(),
                notes=_text(notes.value),
            )
        )

    actions: list[ft.Control] = []

    if on_delete is not None:
        actions.append(ft.TextButton(content="Delete", on_click=lambda _: on_delete()))

    actions.extend(
        [
            ft.TextButton(content="Cancel", on_click=lambda _: on_cancel()),
            ft.Button(content=("Save" if editing else "Add racket"), on_click=submit),
        ]
    )

    return ft.AlertDialog(
        modal=True,
        scrollable=True,
        title=ft.Text("Edit racket" if editing else "Add racket"),
        content=ft.Column(
            spacing=14,
            controls=[image_picker, name, brand, model, notes],
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
            ft.TextButton(content="Cancel", on_click=lambda _: on_cancel()),
            ft.Button(content="Delete", on_click=lambda _: on_confirm()),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )


def _build_image_picker(*, initial_image_id: str) -> tuple[ft.Control, Callable[[], str]]:
    selected_image_id = initial_image_id

    tiles: dict[str, ft.Container] = {}

    picker = ft.Row(spacing=8, scroll=ft.ScrollMode.HIDDEN, controls=[])

    def select_image(image_id: str) -> None:
        nonlocal selected_image_id

        selected_image_id = image_id

        for option_id, tile in tiles.items():
            selected = option_id == selected_image_id

            tile.bgcolor = PRIMARY_SOFT if selected else SURFACE
            tile.border = ft.Border.all(2 if selected else 1, PRIMARY if selected else OUTLINE)

        picker.update()

    for racket_image in RACKET_IMAGES:
        selected = racket_image.id == selected_image_id

        tile = ft.Container(
            width=82,
            height=112,
            padding=6,
            bgcolor=(PRIMARY_SOFT if selected else SURFACE),
            border=ft.Border.all(2 if selected else 1, PRIMARY if selected else OUTLINE),
            border_radius=12,
            ink=True,
            on_click=lambda _, image_id=racket_image.id: select_image(image_id),
            content=ft.Column(
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=(ft.CrossAxisAlignment.CENTER),
                spacing=4,
                controls=[
                    build_racket_image(racket_image.id, width=54, height=76),
                    ft.Text(
                        racket_image.label,
                        size=10,
                        color=TEXT_SECONDARY,
                        text_align=ft.TextAlign.CENTER,
                        max_lines=1,
                    ),
                ],
            ),
        )

        tiles[racket_image.id] = tile
        picker.controls.append(tile)

    return (
        ft.Column(
            spacing=8,
            controls=[
                ft.Text("Racket image", size=13, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                picker,
            ],
        ),
        lambda: selected_image_id,
    )


def _initial_image_id(racket: Racket | None) -> str:
    if racket is not None and racket.image_id and racket.image_id in RACKET_IMAGES:
        return racket.image_id

    return DEFAULT_RACKET_IMAGE_ID


def _text(value: str | None) -> str:
    return (value or "").strip()
