"""Toilet entity — bowl, rim, base."""

import pygame

from game.settings import (
    BOWL_WHITE, BOWL_RIM, TOILET_BASE, WATER_COLOUR, DARK_BLUE,
    TOILET_CENTRE_X, TOILET_CENTRE_Y, BOWL_RADIUS_X, BOWL_RADIUS_Y,
)


class Toilet:
    """The toilet. Bowl is the target zone."""

    def __init__(self) -> None:
        self.centre_x = TOILET_CENTRE_X
        self.centre_y = TOILET_CENTRE_Y
        self.bowl_rx = BOWL_RADIUS_X
        self.bowl_ry = BOWL_RADIUS_Y

        # Collision rect (bounding box for quick reject)
        self.bowl_rect = pygame.Rect(
            self.centre_x - self.bowl_rx,
            self.centre_y - self.bowl_ry,
            self.bowl_rx * 2,
            self.bowl_ry * 2,
        )

        # Water zone — the actual scoring target (tight circle at bowl centre).
        # Outer bowl is visual only; particles must reach this zone to score.
        self.centre_rx: float = 45.0
        self.centre_ry: float = 45.0

    def is_in_bowl(self, x: float, y: float) -> bool:
        """Check if a point is inside the water area (bowl minus rim)."""
        rx = self.bowl_rx - 8
        ry = self.bowl_ry - 8
        dx = (x - self.centre_x) / rx
        dy = (y - self.centre_y) / ry
        return (dx * dx + dy * dy) <= 1.0

    def is_in_centre(self, x: float, y: float) -> bool:
        """Check if a point is in the centre scoring zone (ellipse)."""
        dx = (x - self.centre_x) / self.centre_rx
        dy = (y - self.centre_y) / self.centre_ry
        return (dx * dx + dy * dy) <= 1.0

    def draw(self, surface: pygame.Surface) -> None:
        """Draw toilet from top-down view."""
        # Toilet base/tank (rectangle behind bowl)
        base_rect = pygame.Rect(0, 0, self.bowl_rx * 2 + 40, 50)
        base_rect.center = (self.centre_x, self.centre_y - self.bowl_ry - 20)
        pygame.draw.rect(surface, TOILET_BASE, base_rect, border_radius=8)
        pygame.draw.rect(surface, BOWL_RIM, base_rect, width=2, border_radius=8)

        # Seat (larger ellipse behind bowl)
        seat_rect = pygame.Rect(0, 0, self.bowl_rx * 2 + 24, self.bowl_ry * 2 + 24)
        seat_rect.center = (self.centre_x, self.centre_y)
        pygame.draw.ellipse(surface, TOILET_BASE, seat_rect)
        pygame.draw.ellipse(surface, BOWL_RIM, seat_rect, width=2)

        # Rim (slightly larger than bowl)
        rim_rect = pygame.Rect(0, 0, self.bowl_rx * 2 + 8, self.bowl_ry * 2 + 8)
        rim_rect.center = (self.centre_x, self.centre_y)
        pygame.draw.ellipse(surface, BOWL_RIM, rim_rect)

        # Bowl opening (the target zone)
        bowl_rect = pygame.Rect(0, 0, self.bowl_rx * 2, self.bowl_ry * 2)
        bowl_rect.center = (self.centre_x, self.centre_y)
        pygame.draw.ellipse(surface, BOWL_WHITE, bowl_rect)

        # Water in bowl
        water_rect = pygame.Rect(0, 0, self.bowl_rx * 2 - 16, self.bowl_ry * 2 - 16)
        water_rect.center = (self.centre_x, self.centre_y)
        pygame.draw.ellipse(surface, WATER_COLOUR, water_rect)

        # Scoring hitbox outline
        hitbox_rect = pygame.Rect(
            0, 0,
            int(self.centre_rx * 2), int(self.centre_ry * 2),
        )
        hitbox_rect.center = (self.centre_x, self.centre_y)
        pygame.draw.ellipse(surface, DARK_BLUE, hitbox_rect, width=2)
