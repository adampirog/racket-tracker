from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class RacketImage:
    id: str
    label: str
    path: str


RACKET_IMAGES = (
    RacketImage(id="tfight", label="Tecnifibre TFight 305s", path="rackets/tfight.webp"),
    RacketImage(id="vcore", label="Yonex Vcore", path="rackets/vcore.webp"),
    RacketImage(id="gravity", label="Head Gravity", path="rackets/gravity.webp"),
    RacketImage(id="aero", label="Babolat Pure Aero", path="rackets/aero.webp"),
)

RACKET_IMAGES_BY_ID = {racket.id: racket for racket in RACKET_IMAGES}


DEFAULT_RACKET_IMAGE_ID = "gravity"


def get_racket_image(image_id: str) -> RacketImage:
    return RACKET_IMAGES_BY_ID.get(image_id, RACKET_IMAGES_BY_ID[DEFAULT_RACKET_IMAGE_ID])
