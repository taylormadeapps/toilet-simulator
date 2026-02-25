"""Heads-up display — bladder meter, score."""

import pygame

from game.settings import (
    SCREEN_WIDTH, HUD_BLADDER_FULL, HUD_BLADDER_EMPTY,
    HUD_TEXT, HUD_BG, WHITE, BLACK,
)


class HUD:
    """Draws bladder meter and score during gameplay."""

    def __init__(self) -> None:
        self.font = pygame.font.SysFont("Arial", 24, bold=True)
        self.font_small = pygame.font.SysFont("Arial", 18)

    def draw(self, surface: pygame.Surface, bladder_pct: float, score: int) -> None:
        """Draw all HUD elements."""
        self._draw_bladder_meter(surface, bladder_pct)
        self._draw_score(surface, score)

    def _draw_bladder_meter(self, surface: pygame.Surface,
                            bladder_pct: float) -> None:
        """Vertical bar on the left side of screen."""
        bar_x = 20
        bar_y = 180
        bar_w = 24
        bar_h = 200

        # Background
        pygame.draw.rect(surface, HUD_BG, (bar_x, bar_y, bar_w, bar_h))
        pygame.draw.rect(surface, (80, 80, 90), (bar_x, bar_y, bar_w, bar_h), 2)

        # Fill (bottom-up)
        fill_h = int(bar_h * bladder_pct)
        fill_y = bar_y + bar_h - fill_h
        colour = _lerp_colour(HUD_BLADDER_EMPTY, HUD_BLADDER_FULL, bladder_pct)
        if fill_h > 0:
            pygame.draw.rect(surface, colour,
                             (bar_x + 2, fill_y + 2, bar_w - 4, fill_h - 4))

        # Label
        label = self.font_small.render("BLADDER", True, HUD_TEXT)
        label_rect = label.get_rect(centerx=bar_x + bar_w // 2, top=bar_y + bar_h + 6)
        surface.blit(label, label_rect)

    def _draw_score(self, surface: pygame.Surface, score: int) -> None:
        """Score display in top-right corner."""
        text = self.font.render(f"Score: {score}", True, WHITE)
        rect = text.get_rect(topright=(SCREEN_WIDTH - 20, 20))
        # Drop shadow
        shadow = self.font.render(f"Score: {score}", True, BLACK)
        shadow_rect = shadow.get_rect(topright=(SCREEN_WIDTH - 18, 22))
        surface.blit(shadow, shadow_rect)
        surface.blit(text, rect)


def _lerp_colour(c1: tuple, c2: tuple, t: float) -> tuple[int, int, int]:
    """Linear interpolation between two RGB colours."""
    t = max(0.0, min(1.0, t))
    return (
        int(c1[0] + (c2[0] - c1[0]) * t),
        int(c1[1] + (c2[1] - c1[1]) * t),
        int(c1[2] + (c2[2] - c1[2]) * t),
    )
