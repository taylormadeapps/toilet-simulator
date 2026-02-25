"""Player entity — the belly and stream origin."""

import pygame

from game.settings import (
    SKIN_COLOUR, SKIN_SHADOW, SHIRT_COLOUR,
    BELLY_CENTRE_X, BELLY_CENTRE_Y, BELLY_RADIUS_X, BELLY_RADIUS_Y,
    STREAM_ORIGIN_X, STREAM_ORIGIN_Y,
)


class Player:
    """The big belly at the top of the screen. Stationary."""

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

        # Belly shadow (lower arc for depth)
        shadow_rect = pygame.Rect(0, 0, self.belly_rx * 2 - 20, self.belly_ry + 10)
        shadow_rect.center = (self.belly_cx, self.belly_cy + 30)
        pygame.draw.ellipse(surface, SKIN_SHADOW, shadow_rect)
