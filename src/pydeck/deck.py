from __future__ import annotations

import logging

from StreamDeck.DeviceManager import DeviceManager
from StreamDeck.Devices.StreamDeck import StreamDeck

from pydeck.actions import execute_action
from pydeck.images import blank_key_image, render_key_image
from pydeck.types import PageConfig, PluginContext, PydeckConfig

logger = logging.getLogger(__name__)


def find_deck() -> StreamDeck:
    decks = DeviceManager().enumerate()
    if not decks:
        raise RuntimeError("No Stream Deck devices found")

    deck = decks[0]
    deck.open()
    logger.info(
        "Found: %s (serial: %s)", deck.deck_type(), deck.get_serial_number()
    )
    return deck


def setup_deck(deck: StreamDeck, config: PydeckConfig) -> None:
    deck.reset()

    pages = config.get("pages", [])
    if pages:
        apply_page(deck, pages[0], config)


def apply_page(deck: StreamDeck, page: PageConfig, config: PydeckConfig) -> None:
    brightness = page.get("brightness", 80)
    deck.set_brightness(brightness)
    logger.info(
        "Applying page '%s' (brightness: %d)",
        page.get("name", "unnamed"),
        brightness,
    )

    # Set all keys to blank first
    for i in range(deck.key_count()):
        deck.set_key_image(i, blank_key_image(deck))

    # Apply configured buttons
    buttons = page.get("buttons", {})
    for idx, button in buttons.items():
        if "icon" in button:
            image = render_key_image(deck, button["icon"])
            deck.set_key_image(idx, image)

    # Register key callback
    def key_callback(deck: StreamDeck, key: int, state: bool) -> None:
        logger.debug("Key %d %s", key, "pressed" if state else "released")
        if not state:  # Only act on key press
            return

        button = buttons.get(key)
        if button and "action" in button:
            context = PluginContext(
                deck_id=deck.id(),
                deck_type=deck.deck_type(),
                serial_number=deck.get_serial_number(),
                key_index=key,
                key_state=state,
                config=dict(config),
            )
            execute_action(button["action"], context)

    deck.set_key_callback(key_callback)


def shutdown(deck: StreamDeck) -> None:
    logger.info("Shutting down deck")
    try:
        deck.reset()
        deck.close()
    except Exception:
        logger.exception("Error during deck shutdown")
