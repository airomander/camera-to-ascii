import sys
import ctypes
from pathlib import Path
from datetime import datetime

_FROZEN = getattr(sys, "frozen", False)

if _FROZEN:
    APP_ROOT = Path(sys.executable).resolve().parent
else:
    APP_ROOT = Path(__file__).resolve().parent.parent
    _root = str(APP_ROOT)
    if _root not in sys.path:
        sys.path.insert(0, _root)

import pygame
import numpy as np

from src.camera.webcam import Webcam
from src.converter.ascii_converter import AsciiConverter
from src.converter.modes import (
    ClassicMode, EdgeMode, NegativeMode,
    MatrixMode, ThermalMode, KaleidoMode,
)
from src.renderer.pygame_display import PygameDisplay
from src.config import COLS, FPS_LIMIT, CHAR_SET, FONT_NAME, FONT_SIZE, CAMERA_INDEX

MODES = [
    ClassicMode(),
    EdgeMode(),
    NegativeMode(),
    MatrixMode(),
    ThermalMode(),
    KaleidoMode(),
]


def save_screenshot(screen: pygame.Surface) -> str:
    shots_dir = APP_ROOT / "screenshots"
    shots_dir.mkdir(exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = shots_dir / f"screenshot_{stamp}.png"
    pygame.image.save(screen, str(path))
    return str(path)


def _fatal(msg: str) -> None:
    if _FROZEN:
        ctypes.windll.user32.MessageBoxW(0, msg, "CamASCII Error", 0x10)
    else:
        print(f"Error: {msg}")
    sys.exit(1)


def main() -> None:
    try:
        camera = Webcam(CAMERA_INDEX)
    except RuntimeError as e:
        _fatal(str(e))

    converter = AsciiConverter(CHAR_SET)

    frame = camera.get_frame()
    if frame is None:
        camera.release()
        _fatal("Could not read frame from camera")

    h, w = frame.shape[:2]
    rows = max(1, int(COLS * (h / w) * 0.5))

    display = PygameDisplay(COLS, rows, MODES, FONT_NAME, FONT_SIZE, CHAR_SET)
    clock = pygame.time.Clock()
    active_idx = 0
    last_saved = None

    try:
        while not display.should_quit():
            action = display.poll()

            if action:
                kind, idx = action
                if kind == "mode" and idx != active_idx:
                    active_idx = idx
                    display.set_mode(idx, MODES[idx])
                elif kind == "screenshot":
                    path = save_screenshot(display.screen)
                    last_saved = path

            frame = camera.get_frame()
            if frame is None:
                continue

            mode = MODES[active_idx]

            content = mode.process(frame, converter, COLS, rows)
            display.render(content, mode)
            clock.tick(FPS_LIMIT)

    finally:
        camera.release()
        display.close()


if __name__ == "__main__":
    main()
