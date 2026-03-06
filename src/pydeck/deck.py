from __future__ import annotations

import logging
from typing import Any, Mapping

from StreamDeck.DeviceManager import DeviceManager
from StreamDeck.Devices.StreamDeck import StreamDeck

from pydeck.actions import execute_action
from pydeck.animations import AnimationManager
from pydeck.images import blank_key_image, load_gif_frames, render_key_image
from pydeck.types import PageConfig, PluginContext, PydeckConfig

logger = logging.getLogger(__name__)

_animation_manager: AnimationManager | None = None
_button_states: dict[int, int] = {}


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
    global _animation_manager
    deck.reset()

    _animation_manager = AnimationManager(deck)
    _animation_manager.start()

    pages = config.get("pages", [])
    if pages:
        apply_page(deck, pages[0], config)


def apply_page(deck: StreamDeck, page: PageConfig, config: PydeckConfig) -> None:
    global _button_states

    if _animation_manager:
        _animation_manager.clear_all()
    _button_states = {}

    brightness = page.get("brightness", 80)
    deck.set_brightness(brightness)
    logger.info(
        "Applying page '%s' (brightness: %d)",
        page.get("name", "unnamed"),
        brightness,
    )

    for i in range(deck.key_count()):
        deck.set_key_image(i, blank_key_image(deck))

    buttons = page.get("buttons", {})
    for idx, button in buttons.items():
        if "states" in button:
            _button_states[idx] = 0
            _apply_button_icon(deck, idx, button["states"][0])
        else:
            _apply_button_icon(deck, idx, button)

    def key_callback(deck: StreamDeck, key: int, state: bool) -> None:
        logger.debug("Key %d %s", key, "pressed" if state else "released")
        if not state:
            return

        button = buttons.get(key)
        if not button:
            return

        context = PluginContext(
            deck_id=deck.id(),
            deck_type=deck.deck_type(),
            serial_number=deck.get_serial_number(),
            key_index=key,
            key_state=state,
            config=dict(config),
        )

        if "states" in button:
            _handle_stateful_press(deck, key, button, context)
        else:
            _handle_simple_press(deck, key, button, context)

    deck.set_key_callback(key_callback)


_ButtonLike = Mapping[str, Any]


def _apply_button_icon(
    deck: StreamDeck, key: int, button_or_state: _ButtonLike,
) -> None:
    icon = button_or_state.get("icon", "")
    if not icon:
        return

    if icon.lower().endswith(".gif"):
        frames = load_gif_frames(deck, icon)
        if frames and _animation_manager:
            _animation_manager.set_animation(key, frames, loop=True)
        elif not frames:
            deck.set_key_image(key, blank_key_image(deck))
    else:
        if _animation_manager:
            _animation_manager.clear(key)
        image = render_key_image(deck, icon)
        deck.set_key_image(key, image)


def _handle_stateful_press(
    deck: StreamDeck, key: int, button: _ButtonLike, context: PluginContext
) -> None:
    states = button["states"]
    current = _button_states.get(key, 0)
    current_state = states[current]

    if "action" in current_state:
        execute_action(current_state["action"], context)

    next_idx = (current + 1) % len(states)
    _button_states[key] = next_idx
    next_state = states[next_idx]
    logger.info("Key %d → state '%s'", key, next_state.get("name", next_idx))
    _apply_button_icon(deck, key, next_state)


def _handle_simple_press(
    deck: StreamDeck, key: int, button: _ButtonLike, context: PluginContext
) -> None:
    if "action" in button:
        execute_action(button["action"], context)

    pressed_icon = button.get("pressed_icon", "")
    if not pressed_icon:
        return

    if pressed_icon.lower().endswith(".gif"):
        frames = load_gif_frames(deck, pressed_icon)
        if frames and _animation_manager:
            def restore(
                dk: StreamDeck = deck, k: int = key, b: _ButtonLike = button,
            ) -> None:
                _apply_button_icon(dk, k, b)

            _animation_manager.set_animation(
                key, frames, loop=False, on_complete=restore,
            )
    else:
        if _animation_manager:
            _animation_manager.clear(key)
        image = render_key_image(deck, pressed_icon)
        deck.set_key_image(key, image)


def shutdown(deck: StreamDeck) -> None:
    global _animation_manager
    logger.info("Shutting down deck")
    if _animation_manager:
        _animation_manager.stop()
        _animation_manager = None
    try:
        deck.reset()
        deck.close()
    except Exception:
        logger.exception("Error during deck shutdown")
