from __future__ import annotations

import logging
import threading
import time
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class Animation:
    frames: list[tuple[bytes, int]]  # (native_image, duration_ms)
    loop: bool = True
    on_complete: object | None = None  # callable or None
    frame_index: int = field(default=0, init=False)
    next_frame_time: float = field(default=0.0, init=False)
    finished: bool = field(default=False, init=False)


class AnimationManager:
    def __init__(self, deck) -> None:  # type: ignore[no-untyped-def]
        self._deck = deck
        self._animations: dict[int, Animation] = {}
        self._lock = threading.Lock()
        self._running = False
        self._thread: threading.Thread | None = None

    def set_animation(
        self,
        key: int,
        frames: list[tuple[bytes, int]],
        loop: bool = True,
        on_complete: object | None = None,
    ) -> None:
        if not frames:
            return
        with self._lock:
            anim = Animation(frames=frames, loop=loop, on_complete=on_complete)
            anim.next_frame_time = time.monotonic()
            self._animations[key] = anim
            logger.debug(
                "Animation set for key %d (%d frames, loop=%s)",
                key, len(frames), loop,
            )

    def clear(self, key: int) -> None:
        with self._lock:
            self._animations.pop(key, None)

    def clear_all(self) -> None:
        with self._lock:
            self._animations.clear()

    def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        logger.debug("Animation manager started")

    def stop(self) -> None:
        self._running = False
        if self._thread:
            self._thread.join(timeout=2.0)
            self._thread = None
        self.clear_all()
        logger.debug("Animation manager stopped")

    def _run(self) -> None:
        while self._running:
            now = time.monotonic()
            callbacks = []

            with self._lock:
                for key, anim in list(self._animations.items()):
                    if anim.finished or now < anim.next_frame_time:
                        continue

                    frame_data, duration = anim.frames[anim.frame_index]
                    try:
                        self._deck.set_key_image(key, frame_data)
                    except Exception:
                        logger.exception("Error setting frame for key %d", key)
                        continue

                    anim.frame_index += 1
                    anim.next_frame_time = now + duration / 1000.0

                    if anim.frame_index >= len(anim.frames):
                        if anim.loop:
                            anim.frame_index = 0
                        else:
                            anim.finished = True
                            if anim.on_complete:
                                callbacks.append(anim.on_complete)
                            del self._animations[key]

            for cb in callbacks:
                try:
                    cb()  # type: ignore[operator]
                except Exception:
                    logger.exception("Error in animation on_complete callback")

            time.sleep(0.02)
