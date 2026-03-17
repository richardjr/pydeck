#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
CONFIG_DIR="${HOME}/.config/pydeck"
DESKTOP_DIR="${HOME}/.local/share/applications"
ICON_DIR="${DESKTOP_DIR}/icons"
VENV_DIR="${REPO_DIR}/.venv"
BINARY="${VENV_DIR}/bin/pydeck"

echo "==> Installing pydeck..."

# Create venv and install
if ! command -v uv &>/dev/null; then
    echo "Error: uv is not installed. Install it first: https://docs.astral.sh/uv/"
    exit 1
fi

uv venv "${VENV_DIR}" --python 3.11
uv pip install -e "${REPO_DIR}" --python "${VENV_DIR}/bin/python"

# Seed default config if it doesn't exist
if [ ! -f "${CONFIG_DIR}/default.yaml" ]; then
    echo "==> Seeding default config to ${CONFIG_DIR}..."
    mkdir -p "${CONFIG_DIR}/icons" "${CONFIG_DIR}/plugins"
    cp "${REPO_DIR}/examples/default.yaml" "${CONFIG_DIR}/default.yaml"
    cp "${REPO_DIR}/examples/plugins/"* "${CONFIG_DIR}/plugins/" 2>/dev/null || true
    echo "    Edit ${CONFIG_DIR}/default.yaml to customize your buttons."
    echo "    Add your icon PNGs/GIFs to ${CONFIG_DIR}/icons/"
else
    echo "==> Config already exists at ${CONFIG_DIR}/default.yaml, skipping."
fi

# Install udev rules for Stream Deck
if [ -f "${REPO_DIR}/udev/99-streamdeck.rules" ]; then
    echo "==> Installing udev rules (requires sudo)..."
    sudo cp "${REPO_DIR}/udev/99-streamdeck.rules" /etc/udev/rules.d/
    sudo udevadm control --reload-rules
    sudo udevadm trigger
fi

# Install .desktop entry
echo "==> Installing .desktop entry..."
mkdir -p "${DESKTOP_DIR}" "${ICON_DIR}"

cat > "${DESKTOP_DIR}/pydeck.desktop" <<EOF
[Desktop Entry]
Version=1.0
Name=PyDeck
Comment=Stream Deck Mini client
Exec=${BINARY}
Terminal=false
Type=Application
Icon=input-gaming
Categories=Utility;
StartupNotify=false
EOF

# Update desktop database if available
if command -v update-desktop-database &>/dev/null; then
    update-desktop-database "${DESKTOP_DIR}" 2>/dev/null || true
fi

echo "==> Done! PyDeck is now available in your app launcher (Super+Space)."
