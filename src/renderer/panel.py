import pygame


PANEL_HEIGHT = 42
BTN_PAD = 8
BTN_MARGIN = 4
BTN_RADIUS = 5


class Panel:
    def __init__(self, screen_width: int, modes: list):
        self.rect = pygame.Rect(0, 0, screen_width, PANEL_HEIGHT)
        self.visible = True
        self.modes = modes
        self._font = pygame.font.SysFont("Segoe UI", 12)
        self._buttons = []
        self._hover_idx = -1

        x = BTN_MARGIN
        for i, m in enumerate(modes):
            label = f"[{m.key}] {m.name}"
            tw = self._font.size(label)[0]
            w = tw + BTN_PAD * 2
            self._buttons.append(dict(
                rect=pygame.Rect(x, BTN_MARGIN, w, PANEL_HEIGHT - BTN_MARGIN * 2),
                label=label, action="mode", index=i))
            x += w + BTN_MARGIN

        scr = "[SPACE] Screenshot"
        tw = self._font.size(scr)[0]
        x = screen_width - tw - BTN_PAD * 2 - BTN_MARGIN
        self._buttons.append(dict(
            rect=pygame.Rect(x, BTN_MARGIN, tw + BTN_PAD * 2,
                             PANEL_HEIGHT - BTN_MARGIN * 2),
            label=scr, action="screenshot", index=-1))

    def handle_event(self, event):
        if not self.visible:
            return None
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for b in self._buttons:
                if b["rect"].collidepoint(event.pos):
                    return b["action"], b["index"]
        elif event.type == pygame.MOUSEMOTION:
            self._hover_idx = next(
                (i for i, b in enumerate(self._buttons)
                 if b["rect"].collidepoint(event.pos)), -1)
        return None

    def draw(self, screen, active_idx: int, mode):
        if not self.visible:
            return
        pygame.draw.rect(screen, mode.panel_bg, self.rect)
        pygame.draw.line(screen, (55, 55, 60), (0, 0),
                         (self.rect.width, 0), 1)

        for i, b in enumerate(self._buttons):
            if b["action"] == "screenshot":
                bg = mode.panel_hover if self._hover_idx == i else mode.panel_bg
                fc = (255, 255, 255) if self._hover_idx == i else mode.panel_text
            elif b["index"] == active_idx:
                bg = mode.panel_active
                fc = (255, 255, 255)
            elif self._hover_idx == i:
                bg = mode.panel_hover
                fc = (255, 255, 255)
            else:
                bg = mode.panel_bg
                fc = mode.panel_text

            if bg != mode.panel_bg:
                pygame.draw.rect(screen, bg, b["rect"],
                                 border_radius=BTN_RADIUS)

            surf = self._font.render(b["label"], True, fc)
            screen.blit(surf, surf.get_rect(center=b["rect"].center))
