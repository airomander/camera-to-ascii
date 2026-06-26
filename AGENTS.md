# AGENTS.md — camera-to-ascii

## Commands

```bash
# run from project root (camera-to-ascii/)
python -m src.main              # launch app (requires webcam) — use -m, not src/main.py
python -m pytest tests/ -v      # all 9 tests, no fixtures, offline
```

## Keyboard reference

| Key | Action |
|-----|--------|
| `ESC` / `Q` | Quit |
| `1`–`6` | Switch render mode |
| `H` | Toggle bottom panel |
| `SPACE` | Save screenshot to `screenshots/` |

## Modes (src/converter/modes.py)

| Key | Mode | Process | Visual style |
|-----|------|---------|-------------|
| `1` | Classic | standard | white on black |
| `2` | Edge | Canny + invert | pencil sketch on paper-like bg |
| `3` | Negative | 255−frame | black text on white |
| `4` | Matrix | standard + rain | green neon, falling trails |
| `5` | Thermal | per-char palette | heat map (blue→red) |
| `6` | Kaleidoscope | quadrant mirror | symmetrical patterns |

Adding a new mode: subclass `BaseMode` in `src/converter/modes.py`, override `process()`, define style colours (`bg_color`, `panel_bg`/`text`/`active`/`hover`), add instance to `MODES` list in `src/main.py`.

## Dependency quirk
Use `pygame-ce` (PyPI name) not `pygame`. Standard pygame does not build on Python 3.14. Import is still `import pygame`.

## Architecture

```
camera/webcam.py ──▶ converter/ascii_converter.py ──▶ renderer/pygame_display.py
                          └─ converter/modes.py             └─ renderer/panel.py
                                          (process + colours)    (UI bar at bottom)
```

`main.py` owns the loop: `poll events → camera frame → mode.process(frame) → display.render(indices, colours)`.

`config.py` is the single settings file (COLS=160, FPS_LIMIT=30, etc.).

## Non-obvious facts

- **OpenCV uses BGR**, not RGB. Converter calls `COLOR_BGR2GRAY`.
- **Row auto-calc**: `rows = cols * (h/w) * 0.5` — the 0.5 compensates for font aspect ratio (~2:1 tall). Defined in `ascii_converter.py:24` and `main.py:27`.
- **No linter/formatter/typechecker**. Follow existing style (no comments, type hints on public methods).
- **Colour modes (Matrix, Thermal)** use per-frame surface cache — first frame may be slower.
- **Tests run offline**, no camera or mocking needed.
