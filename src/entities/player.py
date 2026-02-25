"""Player entity — the belly and stream origin."""

import math

import pygame

from game.settings import (
    SKIN_COLOUR, SKIN_SHADOW, SHIRT_COLOUR,
    BELLY_CENTRE_X, BELLY_CENTRE_Y, BELLY_RADIUS_X, BELLY_RADIUS_Y,
    STREAM_ORIGIN_X, STREAM_ORIGIN_Y,
)

# Moob colours — slightly pinker than belly skin
MOOB_COLOUR = (230, 180, 148)
MOOB_SHADOW = (205, 158, 128)
NIPPLE_COLOUR = (195, 140, 115)
CHEST_HAIR = (90, 65, 45)


class Player:
    """The big belly at the bottom of the screen. Stationary."""

    def __init__(self) -> None:
        self.belly_cx = BELLY_CENTRE_X
        self.belly_cy = BELLY_CENTRE_Y
        self.belly_rx = BELLY_RADIUS_X
        self.belly_ry = BELLY_RADIUS_Y
        self.stream_origin = (STREAM_ORIGIN_X, STREAM_ORIGIN_Y)

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the belly from a top-down perspective."""
        # Shirt edge (slightly larger ellipse behind belly)
        shirt_rect = pygame.Rect(0, 0, self.belly_rx * 2 + 30, self.belly_ry * 2 + 20)
        shirt_rect.center = (self.belly_cx, self.belly_cy)
        pygame.draw.ellipse(surface, SHIRT_COLOUR, shirt_rect)

        # Belly (main skin ellipse)
        belly_rect = pygame.Rect(0, 0, self.belly_rx * 2, self.belly_ry * 2)
        belly_rect.center = (self.belly_cx, self.belly_cy)
        pygame.draw.ellipse(surface, SKIN_COLOUR, belly_rect)

        # Belly shadow (upper arc for depth — looking down)
        shadow_rect = pygame.Rect(0, 0, self.belly_rx * 2 - 20, self.belly_ry + 10)
        shadow_rect.center = (self.belly_cx, self.belly_cy - 30)
        pygame.draw.ellipse(surface, SKIN_SHADOW, shadow_rect)

        # --- Moobs (two fleshy mounds at the top of the belly) ---
        moob_rx = 52
        moob_ry = 36
        moob_y = self.belly_cy - self.belly_ry + 20   # sit near top of belly
        moob_spread = 48                                # distance from centre

        for side in (-1, 1):
            mx = self.belly_cx + side * moob_spread
            # Main moob shape
            moob_rect = pygame.Rect(0, 0, moob_rx * 2, moob_ry * 2)
            moob_rect.center = (mx, moob_y)
            pygame.draw.ellipse(surface, MOOB_COLOUR, moob_rect)
            # Underboob shadow crease
            crease_rect = pygame.Rect(0, 0, moob_rx * 2 - 10, moob_ry)
            crease_rect.center = (mx, moob_y + moob_ry // 2 + 4)
            pygame.draw.ellipse(surface, MOOB_SHADOW, crease_rect)
            # Nipple
            pygame.draw.circle(surface, NIPPLE_COLOUR, (mx, moob_y + 4), 5)

        # --- Chest hair ---
        _draw_chest_hair(surface, self.belly_cx, moob_y, moob_spread)


def _draw_chest_hair(
    surface: pygame.Surface, cx: int, cy: int, spread: int,
) -> None:
    """Scatter short curly hairs between and around the moobs."""
    # Deterministic pattern — no randomness, same every frame
    hair_spots = [
        # (offset_x, offset_y, angle_deg, length)
        # Between moobs (the chest valley)
        (0, -8, -20, 8), (0, 0, 15, 7), (0, 8, -10, 9),
        (-6, -4, 30, 7), (6, -4, -30, 7),
        (-4, 12, 10, 8), (4, 12, -15, 8),
        (0, 20, 5, 7), (-5, 24, -20, 6), (5, 24, 25, 6),
        # Around left moob
        (-spread - 10, -10, 40, 6), (-spread + 5, -16, -25, 7),
        (-spread - 15, 8, 15, 6), (-spread + 10, 18, -30, 5),
        # Around right moob
        (spread + 10, -10, -40, 6), (spread - 5, -16, 25, 7),
        (spread + 15, 8, -15, 6), (spread - 10, 18, 30, 5),
        # Below moobs, trailing down belly
        (-12, 34, 10, 7), (0, 36, -5, 8), (12, 34, -12, 7),
        (-8, 46, 20, 6), (8, 46, -20, 6), (0, 50, 0, 7),
    ]
    for ox, oy, angle, length in hair_spots:
        x = cx + ox
        y = cy + oy
        rad = math.radians(angle)
        ex = x + math.cos(rad) * length
        ey = y + math.sin(rad) * length
        pygame.draw.line(surface, CHEST_HAIR, (x, y), (int(ex), int(ey)), 1)
