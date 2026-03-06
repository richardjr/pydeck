from __future__ import annotations

import logging
from pathlib import Path

import yaml

from pydeck.types import PydeckConfig

logger = logging.getLogger(__name__)

DEFAULT_CONFIG_PATH = Path.home() / ".config" / "pydeck" / "default.yaml"
VALID_ACTION_TYPES = {"command", "script", "plugin"}
MAX_BUTTON_INDEX = 5


def load_config(path: Path | None = None) -> PydeckConfig:
    config_path = path or DEFAULT_CONFIG_PATH
    logger.info("Loading config from %s", config_path)

    with open(config_path) as f:
        raw = yaml.safe_load(f)

    if not isinstance(raw, dict):
        raise ValueError(f"Config must be a YAML mapping, got {type(raw).__name__}")

    config = _validate_config(raw, config_path)
    return config


def _resolve_path(base_dir: Path, value: str) -> str:
    p = Path(value).expanduser()
    if not p.is_absolute():
        p = base_dir / p
    return str(p)


def _validate_config(raw: dict, config_path: Path) -> PydeckConfig:  # type: ignore[type-arg]
    config_dir = config_path.parent
    config: PydeckConfig = {}

    # Resolve plugin_dir
    plugin_dir = raw.get("plugin_dir", str(config_dir / "plugins"))
    config["plugin_dir"] = _resolve_path(config_dir, plugin_dir)

    # Resolve icons_dir
    icons_dir = raw.get("icons_dir", str(config_dir / "icons"))
    config["icons_dir"] = _resolve_path(config_dir, icons_dir)

    # Validate pages
    pages = raw.get("pages", [])
    if not isinstance(pages, list) or len(pages) == 0:
        raise ValueError("Config must have at least one page")

    validated_pages = []
    for i, page in enumerate(pages):
        if not isinstance(page, dict):
            raise ValueError(f"Page {i} must be a mapping")
        validated_pages.append(_validate_page(page, config["icons_dir"]))

    config["pages"] = validated_pages  # type: ignore[typeddict-item]
    return config


def _validate_page(page: dict, icons_dir: str) -> dict:  # type: ignore[type-arg]
    result: dict = {}  # type: ignore[type-arg]

    if "name" in page:
        result["name"] = str(page["name"])

    if "brightness" in page:
        brightness = int(page["brightness"])
        if not 0 <= brightness <= 100:
            raise ValueError(f"Brightness must be 0-100, got {brightness}")
        result["brightness"] = brightness

    buttons = page.get("buttons", {})
    if not isinstance(buttons, dict):
        raise ValueError("buttons must be a mapping")

    validated_buttons: dict[int, dict] = {}  # type: ignore[type-arg]
    for key, button in buttons.items():
        idx = int(key)
        if not 0 <= idx <= MAX_BUTTON_INDEX:
            raise ValueError(f"Button index must be 0-{MAX_BUTTON_INDEX}, got {idx}")
        validated_buttons[idx] = _validate_button(button, icons_dir)

    result["buttons"] = validated_buttons
    return result


def _validate_button(button: dict, icons_dir: str) -> dict:  # type: ignore[type-arg]
    result: dict = {}  # type: ignore[type-arg]

    if "icon" in button:
        icon_path = Path(button["icon"])
        if not icon_path.is_absolute():
            icon_path = Path(icons_dir) / icon_path
        result["icon"] = str(icon_path)

    if "action" in button:
        action = button["action"]
        if not isinstance(action, dict):
            raise ValueError("action must be a mapping")
        action_type = action.get("type")
        if action_type not in VALID_ACTION_TYPES:
            raise ValueError(
                f"action type must be one of {VALID_ACTION_TYPES}, got {action_type!r}"
            )
        if "value" not in action:
            raise ValueError("action must have a 'value' field")
        result["action"] = {"type": action_type, "value": action["value"]}

    return result
