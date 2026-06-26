import cv2
import numpy as np


class AsciiConverter:
    def __init__(self, char_set: str = "@%#*+=-:. "):
        self.char_set = char_set
        self.gradient = len(char_set)

    def to_grayscale(self, bgr_frame: np.ndarray) -> np.ndarray:
        return cv2.cvtColor(bgr_frame, cv2.COLOR_BGR2GRAY)

    def map_to_ascii(self, grayscale: np.ndarray) -> np.ndarray:
        indices = grayscale.astype(np.float32) / 255.0 * (self.gradient - 1)
        indices = np.round(indices).astype(np.uint8)
        return np.clip(indices, 0, self.gradient - 1)

    def convert(
        self, frame: np.ndarray, cols: int = 120, rows: int = 0
    ) -> np.ndarray:
        gray = self.to_grayscale(frame)
        h, w = gray.shape
        if rows == 0:
            rows = max(1, int(cols * (h / w) * 0.5))
        resized = cv2.resize(gray, (cols, rows), interpolation=cv2.INTER_LINEAR)
        return self.map_to_ascii(resized)
