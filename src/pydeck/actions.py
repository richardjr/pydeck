from __future__ import annotations

import logging
import subprocess

from pydeck.plugins import call_plugin
from pydeck.types import ActionConfig, PluginContext

logger = logging.getLogger(__name__)


def execute_action(action: ActionConfig, context: PluginContext) -> None:
    action_type = action["type"]
    value = action["value"]

    try:
        if action_type == "command":
            _run_command(value)
        elif action_type == "script":
            _run_script(value)
        elif action_type == "plugin":
            call_plugin(value, context, context.config.get("plugin_dir", ""))
        else:
            logger.error("Unknown action type: %s", action_type)
    except Exception:
        logger.exception("Error executing %s action: %s", action_type, value)


def _run_command(command: str) -> None:
    logger.info("Running command: %s", command)
    subprocess.Popen(
        command,
        shell=True,
        start_new_session=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def _run_script(script_path: str) -> None:
    logger.info("Running script: %s", script_path)
    subprocess.Popen(
        [script_path],
        start_new_session=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
