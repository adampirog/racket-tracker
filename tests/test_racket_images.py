from pathlib import Path

import racket_tracker
from racket_tracker.racket_images import (
    DEFAULT_RACKET_IMAGE_ID,
    RACKET_IMAGES,
    get_racket_image,
    is_racket_image_id,
)


ASSETS_DIR = Path(racket_tracker.__file__).parent.parent / "assets"


def test_racket_image_catalogue_is_valid() -> None:
    ids = [image.id for image in RACKET_IMAGES]

    assert len(ids) == len(set(ids))
    assert DEFAULT_RACKET_IMAGE_ID in ids

    for image in RACKET_IMAGES:
        assert image.id
        assert image.label
        assert (ASSETS_DIR / image.path).is_file()


def test_unknown_racket_image_uses_default() -> None:
    assert not is_racket_image_id("missing")

    assert get_racket_image("missing") == get_racket_image(DEFAULT_RACKET_IMAGE_ID)
