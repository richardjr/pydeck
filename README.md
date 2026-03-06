# pydeck

A Python-based Stream Deck Mini client for Linux. Maps the 6 buttons to shell commands, scripts, or Python plugins via a YAML config. Supports stateful toggle buttons and animated GIF icons.

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
      # Simple button — static icon, single action
      0:
        icon: play-pause.png
        action:
          type: command
          value: "playerctl play-pause"

      # Stateful toggle — cycles through states on each press
      1:
        states:
          - name: unmuted
            icon: mic-on.png
            action:
              type: command
              value: "wpctl set-mute @DEFAULT_AUDIO_SOURCE@ 1"
          - name: muted
            icon: mic-mute.png
            action:
              type: command
              value: "wpctl set-mute @DEFAULT_AUDIO_SOURCE@ 0"

      # Animated button — looping GIF, one-shot press animation
      5:
        icon: lemmings-walk.gif
        pressed_icon: lemmings-explode.gif
        action:
          type: command
          value: "killall firefox Discord"
```

Button indices map to a 2x3 grid:

```
[0] [1] [2]
[3] [4] [5]
```

### Button types

**Simple** — An `icon` (PNG or GIF) and an `action`. Press triggers the action.

**Stateful** — A `states` list (2+). Each state has its own `icon` and `action`. Press executes the current state's action, then advances to the next state. Useful for toggles like mute/unmute.

**Press animation** — A button with `pressed_icon`. On press, plays the pressed icon (typically a one-shot GIF), then returns to the default `icon`. Combine with `action` to run a command at the same time.

### Action types

| Type | Value | Description |
|---|---|---|
| `command` | Shell command string | Runs via shell (e.g. `playerctl play-pause`) |
| `script` | Path to executable | Runs directly (e.g. `~/.config/pydeck/scripts/toggle.sh`) |
| `plugin` | `module:function` | Calls a Python function from `plugin_dir` |

### Icons

Place icons in `icons_dir`. Relative paths in the config resolve against `icons_dir`. Missing icons show as blank keys.

- **PNG** — Static 80x80 images
- **GIF** — Animated, frame durations are preserved. Looping GIFs loop continuously; one-shot GIFs (used as `pressed_icon`) play once then revert.

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
