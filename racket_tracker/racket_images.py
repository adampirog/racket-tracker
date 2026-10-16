from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class RacketImage:
    id: str
    label: str
    path: str


RACKET_IMAGES = (
    RacketImage(id="tfight", label="TFight", path="rackets/tfight.webp"),
    RacketImage(id="vcore", label="Yonex VCORE", path="rackets/vcore.webp"),
    RacketImage(id="gravity", label="Head Gravity", path="rackets/gravity.webp"),
    RacketImage(id="aero", label="Pure Aero", path="rackets/aero.webp"),
)

RACKET_IMAGES_BY_ID = {image.id: image for image in RACKET_IMAGES}

DEFAULT_RACKET_IMAGE_ID = "tfight"


def get_racket_image(image_id: str) -> RacketImage:
    return RACKET_IMAGES_BY_ID.get(image_id, RACKET_IMAGES_BY_ID[DEFAULT_RACKET_IMAGE_ID])


def is_racket_image_id(image_id: str) -> bool:
    return image_id in RACKET_IMAGES_BY_ID
