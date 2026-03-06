from __future__ import annotations

import importlib.util
import logging
import types
from pathlib import Path

from pydeck.types import PluginContext

logger = logging.getLogger(__name__)

_module_cache: dict[str, types.ModuleType] = {}


def call_plugin(ref: str, context: PluginContext, plugin_dir: str) -> None:
    if ":" not in ref:
        raise ValueError(f"Plugin ref must be 'module:function', got {ref!r}")

    module_name, func_name = ref.split(":", 1)
    module = _load_module(module_name, plugin_dir)
    func = getattr(module, func_name)
    logger.info("Calling plugin %s:%s", module_name, func_name)
    func(context)


def _load_module(module_name: str, plugin_dir: str) -> types.ModuleType:
    if module_name in _module_cache:
        return _module_cache[module_name]

    module_path = Path(plugin_dir) / f"{module_name}.py"
    if not module_path.exists():
        raise FileNotFoundError(f"Plugin module not found: {module_path}")

    spec = importlib.util.spec_from_file_location(module_name, module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load plugin module: {module_path}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    _module_cache[module_name] = module
    logger.info("Loaded plugin module: %s", module_path)
    return module


def clear_cache() -> None:
    _module_cache.clear()
    logger.info("Plugin cache cleared")
