import math

import cv2
import numpy as np


class BaseMode:
    render_type = "ascii"

    name = ""
    key = ""
    title = ""
    bg_color = (0, 0, 0)
    panel_bg = (28, 28, 30)
    panel_text = (180, 180, 185)
    panel_active = (65, 65, 70)
    panel_hover = (45, 45, 50)

    def process(self, frame, converter, cols, rows):
        return converter.convert(frame, cols, rows), None

    def on_activate(self):
        pass

    def on_deactivate(self):
        pass


class ClassicMode(BaseMode):
    render_type = "ascii"

    name = "Classic"
    key = "1"
    title = "CamASCII — Classic"
    bg_color = (0, 0, 0)
    panel_bg = (28, 28, 30)
    panel_text = (180, 180, 185)
    panel_active = (65, 65, 70)
    panel_hover = (45, 45, 50)

    def on_activate(self):
        self._drop_state = None


class _ImageMode(BaseMode):
    render_type = "image"

    def process(self, frame, converter=None, cols=0, rows=0):
        return self.process_image(frame)

    def process_image(self, frame):
        return frame


class EdgeMode(_ImageMode):
    name = "Edge"
    key = "2"
    title = "CamASCII — Edge Sketch"
    bg_color = (42, 40, 38)
    panel_bg = (40, 38, 35)
    panel_text = (190, 185, 175)
    panel_active = (80, 72, 62)
    panel_hover = (58, 52, 46)

    def process_image(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blur, 30, 100)
        kernel = np.ones((2, 2), np.uint8)
        edges = cv2.dilate(edges, kernel, iterations=1)
        edges = 255 - edges
        return cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)


class NegativeMode(_ImageMode):
    name = "Negative"
    key = "3"
    title = "CamASCII — Negative"
    bg_color = (235, 235, 235)
    panel_bg = (200, 200, 200)
    panel_text = (30, 30, 30)
    panel_active = (160, 160, 160)
    panel_hover = (180, 180, 180)

    def process_image(self, frame):
        return 255 - frame


class MatrixMode(_ImageMode):
    name = "Matrix"
    key = "4"
    title = "CamASCII — Matrix"
    bg_color = (0, 0, 0)
    panel_bg = (0, 16, 0)
    panel_text = (0, 190, 0)
    panel_active = (0, 55, 0)
    panel_hover = (0, 32, 0)

    def __init__(self):
        self._drop_y = None
        self._drop_v = None
        self._drop_x = None
        self._drop_flash = None
        self._frame = 0
        self._clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))

    def on_activate(self):
        self._drop_y = None
        self._frame = 0

    def process_image(self, frame):
        h, w = frame.shape[:2]
        self._frame += 1

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = self._clahe.apply(gray)

        base = np.zeros((h, w, 3), dtype=np.uint8)
        base[:, :, 1] = (gray * 0.45).astype(np.uint8)

        base[1::2] = (base[1::2] * 0.65).astype(np.uint8)

        if self._drop_y is None:
            n = max(1, w // 2)
            self._drop_y = np.random.randint(-h, 0, size=n).astype(np.float32)
            self._drop_v = np.random.uniform(2.5, 6.0, size=n)
            self._drop_x = np.random.randint(0, w, size=n)
            self._drop_flash = np.random.rand(n) < 0.05

        pulse = 0.85 + 0.15 * math.sin(self._frame * 0.15)

        self._drop_y += self._drop_v * pulse
        overflow = self._drop_y > h
        cnt = overflow.sum()
        if cnt:
            self._drop_y[overflow] = np.random.randint(-h, -15, size=cnt).astype(np.float32)
            self._drop_x[overflow] = np.random.randint(0, w, size=cnt)
            self._drop_flash[overflow] = np.random.rand(cnt) < 0.05

        trail_len = max(3, h // 15)
        step = 255 / max(trail_len, 1)
        x_pos = self._drop_x.astype(int)
        y_pos = self._drop_y.astype(int)

        for i in range(len(self._drop_y)):
            x = x_pos[i]
            if x < 1 or x >= w - 1:
                continue
            dy = y_pos[i]

            for off in range(trail_len):
                py = dy - off * 2
                if py < 0 or py >= h:
                    continue

                b = max(30, int((255 - off * step) * pulse))
                flash = self._drop_flash[i] and off < 3

                if flash:
                    b2 = min(255, b + 60)
                    base[py, x, 0] = max(base[py, x, 0], b2)
                    base[py, x, 1] = max(base[py, x, 1], min(255, b2 + 30))
                    base[py, x, 2] = max(base[py, x, 2], b2)
                elif off == 0:
                    b2 = min(255, b + 40)
                    wv = b // 4
                    base[py, x, 0] = max(base[py, x, 0], wv)
                    base[py, x, 1] = max(base[py, x, 1], b2)
                    base[py, x, 2] = max(base[py, x, 2], wv)
                else:
                    base[py, x, 1] = max(base[py, x, 1], b)

                glow = b // 3 if flash else b // 5
                if glow > 0:
                    base[py, x - 1, 1] = max(base[py, x - 1, 1], glow)
                    base[py, x + 1, 1] = max(base[py, x + 1, 1], glow)

        return base


class ThermalMode(_ImageMode):
    name = "Thermal"
    key = "5"
    title = "CamASCII — Thermal"
    bg_color = (5, 5, 15)
    panel_bg = (20, 8, 8)
    panel_text = (230, 160, 80)
    panel_active = (55, 18, 8)
    panel_hover = (32, 12, 6)

    def __init__(self):
        self._colormap = cv2.COLORMAP_INFERNO

    def process_image(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        return cv2.applyColorMap(gray, self._colormap)


class KaleidoMode(_ImageMode):
    name = "Kaleidoscope"
    key = "6"
    title = "CamASCII — Kaleidoscope"
    bg_color = (0, 0, 0)
    panel_bg = (18, 0, 26)
    panel_text = (190, 170, 220)
    panel_active = (48, 18, 65)
    panel_hover = (30, 8, 42)

    def process_image(self, frame):
        h, w = frame.shape[:2]
        size = min(h, w) // 2
        if size < 4:
            return frame
        cy, cx = h // 2, w // 2
        quad = frame[cy - size : cy, cx - size : cx]
        top = np.hstack([quad, np.fliplr(quad)])
        bot = np.hstack([np.flipud(quad), np.flipud(np.fliplr(quad))])
        return np.vstack([top, bot])
