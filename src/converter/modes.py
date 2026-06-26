import cv2
import numpy as np


class BaseMode:
    name = "Classic"
    key = "1"
    title = "Webcam ASCII Art — Classic"
    bg_color = (0, 0, 0)
    panel_bg = (28, 28, 30)
    panel_text = (180, 180, 185)
    panel_active = (65, 65, 70)
    panel_hover = (45, 45, 50)

    def process(
        self, frame: np.ndarray, converter, cols: int, rows: int
    ) -> tuple:
        return converter.convert(frame, cols, rows), None

    def on_activate(self) -> None:
        pass

    def on_deactivate(self) -> None:
        pass


class ClassicMode(BaseMode):
    name = "Classic"
    key = "1"
    title = "Webcam ASCII Art — Classic"
    bg_color = (0, 0, 0)
    panel_bg = (28, 28, 30)
    panel_text = (180, 180, 185)
    panel_active = (65, 65, 70)
    panel_hover = (45, 45, 50)


class EdgeMode(BaseMode):
    name = "Edge"
    key = "2"
    title = "Webcam ASCII Art — Edge Sketch"
    bg_color = (42, 40, 38)
    panel_bg = (40, 38, 35)
    panel_text = (190, 185, 175)
    panel_active = (80, 72, 62)
    panel_hover = (58, 52, 46)

    def process(self, frame, converter, cols, rows):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blur, 30, 100)
        kernel = np.ones((2, 2), np.uint8)
        edges = cv2.dilate(edges, kernel, iterations=1)
        edges = 255 - edges
        h, w = edges.shape
        if rows == 0:
            rows = max(1, int(cols * (h / w) * 0.5))
        resized = cv2.resize(edges, (cols, rows), interpolation=cv2.INTER_LINEAR)
        indices = converter.map_to_ascii(resized)
        return indices, None


class NegativeMode(BaseMode):
    name = "Negative"
    key = "3"
    title = "Webcam ASCII Art — Negative"
    bg_color = (235, 235, 235)
    panel_bg = (200, 200, 200)
    panel_text = (30, 30, 30)
    panel_active = (160, 160, 160)
    panel_hover = (180, 180, 180)

    def process(self, frame, converter, cols, rows):
        inv = 255 - frame
        indices = converter.convert(inv, cols, rows)
        return indices, None


class MatrixMode(BaseMode):
    name = "Matrix"
    key = "4"
    title = "Webcam ASCII Art — Matrix"
    bg_color = (0, 0, 0)
    panel_bg = (0, 16, 0)
    panel_text = (0, 190, 0)
    panel_active = (0, 55, 0)
    panel_hover = (0, 32, 0)

    def __init__(self):
        self._drops = None
        self._velocities = None

    def on_activate(self):
        self._drops = None
        self._velocities = None

    def process(self, frame, converter, cols, rows):
        gray = converter.to_grayscale(frame)
        h, w = gray.shape
        if rows == 0:
            rows = max(1, int(cols * (h / w) * 0.5))
        resized = cv2.resize(gray, (cols, rows), interpolation=cv2.INTER_LINEAR)
        indices = converter.map_to_ascii(resized)

        colors = np.zeros((rows, cols, 3), dtype=np.uint8)
        g = np.clip(resized.astype(np.int32) * 180 // 255 + 75, 75, 255).astype(np.uint8)
        colors[:, :, 1] = g

        if self._drops is None:
            self._drops = np.random.randint(-rows, 0, size=cols).astype(np.float32)
            self._velocities = np.random.uniform(1.5, 4.5, size=cols)

        self._drops += self._velocities
        overflow = self._drops > rows + 5
        count = overflow.sum()
        if count > 0:
            self._drops[overflow] = np.random.randint(-rows, -5, size=count).astype(np.float32)
            self._velocities[overflow] = np.random.uniform(1.5, 4.5, size=count)

        for x in range(cols):
            dy = int(self._drops[x])
            for off in range(6):
                py = dy - off * 2
                if 0 <= py < rows:
                    b = max(90, 255 - off * 30)
                    colors[py, x] = (0, b, 0)

        return indices, colors


class ThermalMode(BaseMode):
    name = "Thermal"
    key = "5"
    title = "Webcam ASCII Art — Thermal"
    bg_color = (5, 5, 15)
    panel_bg = (20, 8, 8)
    panel_text = (230, 160, 80)
    panel_active = (55, 18, 8)
    panel_hover = (32, 12, 6)

    def __init__(self):
        self._palette = self._build_palette(40)

    @staticmethod
    def _build_palette(n):
        pal = []
        for i in range(n):
            t = i / max(n - 1, 1)
            if t < 0.2:
                a = t / 0.2
                r, g, b = 0, int(a * 120), 255
            elif t < 0.4:
                a = (t - 0.2) / 0.2
                r, g, b = 0, 120 + int(a * 135), 255 - int(a * 180)
            elif t < 0.6:
                a = (t - 0.4) / 0.2
                r, g, b = int(a * 80), 255, 255 - int(a * 180) - int(a * 75)
            elif t < 0.8:
                a = (t - 0.6) / 0.2
                r, g, b = 80 + int(a * 175), 255 - int(a * 120), 0
            else:
                a = (t - 0.8) / 0.2
                r, g, b = 255, 135 - int(a * 135), 0
            pal.append((r, g, b))
        return pal

    def process(self, frame, converter, cols, rows):
        gray = converter.to_grayscale(frame)
        h, w = gray.shape
        if rows == 0:
            rows = max(1, int(cols * (h / w) * 0.5))
        resized = cv2.resize(gray, (cols, rows), interpolation=cv2.INTER_LINEAR)
        indices = converter.map_to_ascii(resized)

        n = len(self._palette)
        flat = resized.ravel().astype(np.int32)
        idxs = np.clip(flat * n // 256, 0, n - 1)
        colors = np.array(self._palette, dtype=np.uint8)[idxs]
        colors = colors.reshape((rows, cols, 3))

        return indices, colors


class KaleidoMode(BaseMode):
    name = "Kaleidoscope"
    key = "6"
    title = "Webcam ASCII Art — Kaleidoscope"
    bg_color = (0, 0, 0)
    panel_bg = (18, 0, 26)
    panel_text = (190, 170, 220)
    panel_active = (48, 18, 65)
    panel_hover = (30, 8, 42)

    def process(self, frame, converter, cols, rows):
        h, w = frame.shape[:2]
        size = min(h, w) // 2
        if size < 4:
            return converter.convert(frame, cols, rows), None
        cy, cx = h // 2, w // 2
        quad = frame[cy - size : cy, cx - size : cx]
        top = np.hstack([quad, np.fliplr(quad)])
        bot = np.hstack([np.flipud(quad), np.flipud(np.fliplr(quad))])
        mirror = np.vstack([top, bot])
        return converter.convert(mirror, cols, rows), None
