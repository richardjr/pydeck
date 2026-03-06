from __future__ import annotations

import logging
from pathlib import Path

from PIL import Image
from StreamDeck.ImageHelpers import PILHelper

logger = logging.getLogger(__name__)


def render_key_image(deck, icon_path: str) -> bytes:  # type: ignore[no-untyped-def]
    path = Path(icon_path)
    if not path.exists():
        logger.warning("Icon not found: %s, using blank", icon_path)
        image = PILHelper.create_key_image(deck)
    else:
        image = Image.open(path)
        image = PILHelper.create_scaled_key_image(deck, image)

    return PILHelper.to_native_key_format(deck, image)  # type: ignore[no-any-return]


def blank_key_image(deck) -> bytes:  # type: ignore[no-untyped-def]
    image = PILHelper.create_key_image(deck)
    return PILHelper.to_native_key_format(deck, image)  # type: ignore[no-any-return]
