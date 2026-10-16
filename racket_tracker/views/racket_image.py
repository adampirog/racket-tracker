import flet as ft

from racket_tracker.racket_images import get_racket_image
from racket_tracker.theme import PRIMARY


def get_default_icon() -> ft.Icon:
    return ft.Icon(ft.Icons.SPORTS_TENNIS, size=58, color=PRIMARY)


def build_racket_image(image_id: str | None, *, width: float, height: float) -> ft.Image | ft.Icon:
    if not image_id:
        return get_default_icon()

    image_path = get_racket_image(image_id)

    return ft.Image(
        src=image_path,
        width=width,
        height=height,
        fit=ft.BoxFit.CONTAIN,
        anti_alias=True,
        semantics_label=f"{image_id} tennis racket",
        error_content=ft.Icon(
            ft.Icons.SPORTS_TENNIS, size=min(width, height) * 0.55, color=PRIMARY
        ),
    )
