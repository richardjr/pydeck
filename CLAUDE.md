# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**pydeck** is a Python-based Stream Deck Mini client for Linux. It loads a YAML config that maps the 6 buttons (2x3 grid, 80x80px icons) to shell commands, scripts, or Python plugins. Supports stateful toggle buttons and animated GIF icons.

## Language & Tooling

- Python >=3.11, src layout (`src/pydeck/`)
- Packaging: uv + hatchling
- Dependencies: `streamdeck`, `Pillow`, `PyYAML`
- Dev: `ruff`, `mypy`, `types-PyYAML`, `types-Pillow`
- Standard Python .gitignore is in place

## Common Commands

```bash
uv venv && uv pip install -e ".[dev]"   # Install
pydeck --help                            # CLI usage
pydeck --config examples/default.yaml    # Run with example config
ruff check src/                          # Lint
mypy src/                                # Type check
```

## Architecture

Flat module design — no class hierarchies. Data flows through TypedDicts and dataclasses.

| Module | Role |
|---|---|
| `cli.py` | Entry point, argparse, signal handlers, main loop |
| `config.py` | YAML loading, validation, path resolution |
| `deck.py` | Device discovery, image application, key callbacks, state management |
| `actions.py` | Action dispatch: command, script, plugin |
| `plugins.py` | importlib-based plugin loader with caching |
| `images.py` | PNG/GIF loading, resize via StreamDeck PILHelper |
| `animations.py` | AnimationManager — background thread cycling GIF frames |
| `types.py` | TypedDicts for config, PluginContext dataclass |

## Config

Default location: `~/.config/pydeck/default.yaml`. Override with `--config`.
Button indices 0-5 map to a 2x3 grid: `[0][1][2]` / `[3][4][5]`.
Action types: `command` (shell), `script` (executable path), `plugin` (module:function).

### Button types

- **Simple**: `icon` + `action` — static or animated icon, single action
- **Stateful**: `states` list — cycles through states on press, each with own icon/action
- **Press animation**: `pressed_icon` — plays a one-shot animation on press, then returns to default icon

Icons can be PNG (static) or GIF (animated). GIF frame durations are preserved.

## System Setup (Arch)

```bash
sudo pacman -S libusb hidapi
sudo cp udev/99-streamdeck.rules /etc/udev/rules.d/
sudo udevadm control --reload-rules && sudo udevadm trigger
```
