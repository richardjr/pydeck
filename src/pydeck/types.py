from __future__ import annotations

from dataclasses import dataclass
from typing import Any, TypedDict


class ActionConfig(TypedDict):
    type: str  # "command" | "script" | "plugin"
    value: str


class ButtonConfig(TypedDict, total=False):
    icon: str
    action: ActionConfig


class PageConfig(TypedDict, total=False):
    name: str
    brightness: int
    buttons: dict[int, ButtonConfig]


class PydeckConfig(TypedDict, total=False):
    plugin_dir: str
    icons_dir: str
    pages: list[PageConfig]


@dataclass
class PluginContext:
    deck_id: str
    deck_type: str
    serial_number: str
    key_index: int
    key_state: bool
    config: dict[str, Any]
