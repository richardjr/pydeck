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


def load_gif_frames(deck, gif_path: str) -> list[tuple[bytes, int]]:  # type: ignore[no-untyped-def]
    """Load a GIF and return list of (native_image_bytes, duration_ms) tuples."""
    path = Path(gif_path)
    if not path.exists():
        logger.warning("GIF not found: %s", gif_path)
        return []

    frames = []
    img = Image.open(path)

    try:
        while True:
            duration = img.info.get("duration", 100)
            frame = img.convert("RGBA")
            scaled = PILHelper.create_scaled_key_image(deck, frame)
            native = PILHelper.to_native_key_format(deck, scaled)
            frames.append((native, duration))
            img.seek(img.tell() + 1)
    except EOFError:
        pass

    logger.debug("Loaded %d frames from %s", len(frames), gif_path)
    return frames


def blank_key_image(deck) -> bytes:  # type: ignore[no-untyped-def]
    image = PILHelper.create_key_image(deck)
    return PILHelper.to_native_key_format(deck, image)  # type: ignore[no-any-return]
