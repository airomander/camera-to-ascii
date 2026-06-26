# AGENTS.md — camera-to-ascii

## Commands

```bash
# run from source
python -m src.main              # requires webcam — use -m, not src/main.py
python -m pytest tests/ -v      # 9 tests, offline, no fixtures

# build standalone exe
.\build.bat                     # produces dist/CamASCII.exe
```

## Keyboard reference

| Key | Action |
|-----|--------|
| `ESC` / `Q` | Quit |
| `1`–`6` | Switch render mode |
| `H` | Toggle bottom panel |
| `SPACE` | Save screenshot to `screenshots/` |

## Modes (src/converter/modes.py)

| Key | Mode | Render | Process |
|-----|------|--------|---------|
| `1` | Classic | ASCII | white on black (original) |
| `2` | Edge | **Image** | Canny + dilation + invert → pencil sketch |
| `3` | Negative | **Image** | 255−frame, white bg / black fg |
| `4` | Matrix | **Image** | green-tinted mono + digital rain trails |
| `5` | Thermal | **Image** | OpenCV `COLORMAP_INFERNO` heat map |
| `6` | Kaleidoscope | **Image** | quadrant mirror → symmetrical patterns |

Modes 2–6 render directly as images (one `blit()` — no freeze). Only `Classic` uses ASCII rendering.

Adding a new mode: subclass `BaseMode` (ASCII) or `_ImageMode` (image), set `render_type`, override `process()` (ascii) or `process_image()` (image), add to `MODES` list in `main.py`.

## Dependency quirk
Use `pygame-ce` (PyPI name) not `pygame`. Standard pygame does not build on Python 3.14. Import is still `import pygame`.

## Architecture

```
camera/webcam.py ──▶ converter/ascii_converter.py ──▶ renderer/pygame_display.py
                          └─ converter/modes.py             └─ renderer/panel.py
                                ascii / image                    UI bar at bottom
```

`main.py` loop: `poll → camera frame → mode.process(frame) → display.render(content, mode)`.
`display.render()` dispatches to `_render_ascii()` or `_render_image()` based on `mode.render_type`.

`config.py` is the single settings file (COLS=160, FPS_LIMIT=30).

## Non-obvious facts

- **OpenCV uses BGR**, not RGB. Converter calls `COLOR_BGR2GRAY`. Image modes do `cv2.cvtColor(..., COLOR_BGR2RGB)` for pygame.
- **Row auto-calc**: `rows = cols * (h/w) * 0.5` — the 0.5 compensates for font aspect ratio (~2:1 tall). Only matters for Classic mode.
- **No linter/formatter/typechecker**. Follow existing style (no comments, type hints on public methods).
- **Image rendering** → one `pygame.transform.scale()` + one `blit()` per frame. No per-character loop → no freeze.
- **PyInstaller build**: `--onefile --noconsole`. `APP_ROOT` = exe dir. Errors shown as MessageBox. See `build.bat`.
- **Tests run offline**, no camera or mocking needed.
