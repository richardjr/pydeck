from __future__ import annotations

import argparse
import logging
import signal
import threading
from pathlib import Path

from pydeck.config import DEFAULT_CONFIG_PATH, load_config
from pydeck.deck import apply_page, find_deck, setup_deck, shutdown
from pydeck.plugins import clear_cache

logger = logging.getLogger("pydeck")

stop_event = threading.Event()
_deck = None
_config = None
_config_path: Path | None = None


def main() -> None:
    global _deck, _config, _config_path

    args = parse_args()
    _setup_logging(args.verbose)

    _config_path = Path(args.config)
    _config = load_config(_config_path)

    if args.brightness is not None:
        for page in _config.get("pages", []):
            page["brightness"] = args.brightness

    _deck = find_deck()
    setup_deck(_deck, _config)

    signal.signal(signal.SIGINT, _handle_stop)
    signal.signal(signal.SIGTERM, _handle_stop)
    signal.signal(signal.SIGHUP, _handle_reload)

    logger.info("pydeck running. Press Ctrl+C to exit.")
    stop_event.wait()

    shutdown(_deck)
    logger.info("Goodbye.")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="pydeck",
        description="Python Stream Deck client",
    )
    parser.add_argument(
        "--config",
        default=str(DEFAULT_CONFIG_PATH),
        help=f"Path to config file (default: {DEFAULT_CONFIG_PATH})",
    )
    parser.add_argument(
        "--brightness",
        type=int,
        choices=range(0, 101),
        metavar="0-100",
        help="Override brightness for all pages",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable debug logging",
    )
    return parser.parse_args()


def _setup_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)-8s %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )


def _handle_stop(signum: int, frame: object) -> None:
    logger.info("Received signal %d, shutting down...", signum)
    stop_event.set()


def _handle_reload(signum: int, frame: object) -> None:
    global _config

    logger.info("Received SIGHUP, reloading config...")
    if _deck is None or _config_path is None:
        return

    try:
        _config = load_config(_config_path)
        clear_cache()
        pages = _config.get("pages", [])
        if pages:
            apply_page(_deck, pages[0], _config)
        logger.info("Config reloaded successfully")
    except Exception:
        logger.exception("Failed to reload config")


if __name__ == "__main__":
    main()
