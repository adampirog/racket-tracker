import flet as ft

from racket_tracker.racket_images import get_racket_image
from racket_tracker.theme import PRIMARY


def get_default_icon(*, size: float = 58) -> ft.Icon:
    return ft.Icon(ft.Icons.SPORTS_TENNIS, size=size, color=PRIMARY)


def build_racket_image(image_id: str, *, width: float, height: float) -> ft.Image:
    image = get_racket_image(image_id)

    return ft.Image(
        src=image.path,
        width=width,
        height=height,
        fit=ft.BoxFit.CONTAIN,
        anti_alias=True,
        semantics_label=f"{image.label} tennis racket",
        error_content=get_default_icon(size=min(width, height) * 0.55),
    )
