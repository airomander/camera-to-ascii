import sys
from pathlib import Path
from datetime import datetime

_root = str(Path(__file__).resolve().parent.parent)
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
    shots_dir = Path(_root) / "screenshots"
    shots_dir.mkdir(exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = shots_dir / f"screenshot_{stamp}.png"
    pygame.image.save(screen, str(path))
    return str(path)


def main() -> None:
    try:
        camera = Webcam(CAMERA_INDEX)
    except RuntimeError as e:
        print(f"Error: {e}")
        sys.exit(1)

    converter = AsciiConverter(CHAR_SET)

    frame = camera.get_frame()
    if frame is None:
        print("Error: Could not read frame from camera")
        camera.release()
        sys.exit(1)

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

            # Process frame through the active mode
            result = mode.process(frame, converter, COLS, rows)
            if len(result) == 2:
                char_indices, colors = result
            else:
                char_indices = result
                colors = None

            display.render(char_indices, colors)
            clock.tick(FPS_LIMIT)

    finally:
        camera.release()
        display.close()


if __name__ == "__main__":
    main()
