"""Example pydeck plugin.

Plugin functions receive a PluginContext dataclass with deck state.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pydeck.types import PluginContext

logger = logging.getLogger(__name__)


def on_press(context: PluginContext) -> None:
    logger.info(
        "Example plugin: key %d pressed on %s",
        context.key_index,
        context.deck_type,
    )
