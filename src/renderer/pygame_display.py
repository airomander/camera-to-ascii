import cv2
import pygame
import numpy as np

from src.renderer.panel import Panel, PANEL_HEIGHT


class PygameDisplay:
    def __init__(
        self,
        cols: int,
        rows: int,
        modes: list,
        font_name: str = "Courier New",
        font_size: int = 12,
        char_set: str = "@%#*+=-:. ",
    ):
        pygame.init()
        self.cols = cols
        self.rows = rows
        self.char_set = char_set

        self.font = pygame.font.SysFont(font_name, font_size)
        self.char_w, self.char_h = self.font.size("W")

        self.ascii_w = self.char_w * cols
        self.ascii_h = self.char_h * rows

        self.panel = Panel(self.ascii_w, modes)

        self.window_w = self.ascii_w
        self.window_h = self.ascii_h + PANEL_HEIGHT

        self.screen = pygame.display.set_mode((self.window_w, self.window_h))

        self._char_surfs = [
            self.font.render(c, True, (255, 255, 255)) for c in char_set
        ]

        self._active_idx = 0
        self._active_mode = modes[0]
        pygame.display.set_caption(self._active_mode.title)

        self.running = True

    def set_mode(self, idx: int, mode) -> None:
        self._active_idx = idx
        self._active_mode = mode
        mode.on_activate()
        pygame.display.set_caption(mode.title)

    def poll(self):
        result = None
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    self.running = False
                elif event.key == pygame.K_h:
                    self.panel.visible = not self.panel.visible
                elif event.key == pygame.K_SPACE:
                    result = ("screenshot", -1)
            elif event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEMOTION):
                r = self.panel.handle_event(event)
                if r:
                    result = r
        return result

    def render(self, content, mode=None) -> None:
        if mode is None:
            mode = self._active_mode

        self.screen.fill(mode.bg_color)

        if mode.render_type == "image":
            self._render_image(content)
        else:
            char_indices, colors = content
            self._render_ascii(char_indices, colors)

        self.panel.draw(self.screen, self._active_idx, mode)
        pygame.display.flip()

    def _render_ascii(self, char_indices: np.ndarray,
                      colors: np.ndarray | None = None) -> None:
        for y in range(min(self.rows, char_indices.shape[0])):
            for x in range(min(char_indices.shape[1], self.cols)):
                idx = int(char_indices[y, x])
                if idx >= len(self.char_set):
                    continue
                self.screen.blit(
                    self._char_surfs[idx],
                    (x * self.char_w, y * self.char_h),
                )

    def _render_image(self, frame_bgr: np.ndarray) -> None:
        h, w = frame_bgr.shape[:2]
        frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)

        scale = min(self.ascii_w / w, self.ascii_h / h)
        nw, nh = int(w * scale), int(h * scale)

        surf = pygame.image.frombuffer(frame_rgb.tobytes(), (w, h), "RGB")
        scaled = pygame.transform.scale(surf, (nw, nh))

        x = (self.ascii_w - nw) // 2
        y = (self.ascii_h - nh) // 2
        self.screen.blit(scaled, (x, y))

    def should_quit(self) -> bool:
        return not self.running

    def close(self) -> None:
        pygame.quit()
