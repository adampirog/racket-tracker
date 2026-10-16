RACKET_IMAGES = {
    "tfight": "rackets/tfight.webp",
    "vcore": "rackets/vcore.webp",
    "gravity": "rackets/gravity.webp",
    "aero": "rackets/aero.webp",
}
DEFAULT_RACKET_IMAGE_ID = "gravity"


def get_racket_image(image_id: str) -> str:
    return RACKET_IMAGES.get(image_id, RACKET_IMAGES[DEFAULT_RACKET_IMAGE_ID])
