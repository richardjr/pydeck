# pydeck

A Python-based Stream Deck Mini client for Linux. Maps the 6 buttons to shell commands, scripts, or Python plugins via a YAML config.

## Prerequisites

Arch Linux:

```bash
sudo pacman -S libusb hidapi
```

### udev rules

Allow non-root access to the Stream Deck:

```bash
sudo cp udev/99-streamdeck.rules /etc/udev/rules.d/
sudo udevadm control --reload-rules && sudo udevadm trigger
```

Replug the Stream Deck after applying.

## Install

```bash
uv venv
uv pip install -e .
```

## Usage

```bash
# Run with default config (~/.config/pydeck/default.yaml)
pydeck

# Run with a specific config
pydeck --config examples/default.yaml

# Override brightness (0-100)
pydeck --brightness 50

# Debug logging
pydeck -v
```

Press Ctrl+C to exit (resets buttons and closes cleanly). Send SIGHUP to reload config without restarting.

## Configuration

Create `~/.config/pydeck/default.yaml`:

```yaml
plugin_dir: ~/.config/pydeck/plugins
icons_dir: ~/.config/pydeck/icons

pages:
  - name: main
    brightness: 80
    buttons:
      0:
        icon: play-pause.png
        action:
          type: command
          value: "playerctl play-pause"
      1:
        icon: mic-mute.png
        action:
          type: command
          value: "wpctl set-mute @DEFAULT_AUDIO_SOURCE@ toggle"
      5:
        icon: custom.png
        action:
          type: plugin
          value: "example_plugin:on_press"
```

Button indices map to a 2x3 grid:

```
[0] [1] [2]
[3] [4] [5]
```

### Action types

| Type | Value | Description |
|---|---|---|
| `command` | Shell command string | Runs via shell (e.g. `playerctl play-pause`) |
| `script` | Path to executable | Runs directly (e.g. `~/.config/pydeck/scripts/toggle.sh`) |
| `plugin` | `module:function` | Calls a Python function from `plugin_dir` |

### Icons

Place 80x80 PNG files in `icons_dir`. Relative paths in the config resolve against `icons_dir`. Missing icons show as blank keys.

## Plugins

Plugins are plain Python files in `plugin_dir` (default `~/.config/pydeck/plugins/`). Reference them as `module_name:function_name` in config.

```python
# ~/.config/pydeck/plugins/my_plugin.py
def on_press(context):
    print(f"Key {context.key_index} pressed on {context.deck_type}")
```

The `context` is a `PluginContext` with: `deck_id`, `deck_type`, `serial_number`, `key_index`, `key_state`, `config`.

Plugins are cached after first load and cleared on SIGHUP reload.

## Development

```bash
uv pip install -e ".[dev]"
ruff check src/
mypy src/
```
