"""Player entity — the belly and stream origin."""

from __future__ import annotations

import math

import pygame

from game.settings import (
    SKIN_COLOUR, SKIN_SHADOW, SHIRT_COLOUR,
    BELLY_CENTRE_X, BELLY_CENTRE_Y, BELLY_RADIUS_X, BELLY_RADIUS_Y,
    STREAM_ORIGIN_X, STREAM_ORIGIN_Y,
)

MOOB_COLOUR = (228, 178, 145)
NIPPLE_COLOUR = (172, 112, 88)
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
        """Draw the player from top-down: trousers, belly, then moob semi-ellipses."""
        belly_top = self.belly_cy - self.belly_ry  # ≈ y 571

        # 1. Trouser/waistband outline — blue ellipse just larger than belly
        waist_rect = pygame.Rect(0, 0, self.belly_rx * 2 + 28, self.belly_ry * 2 + 28)
        waist_rect.center = (self.belly_cx, self.belly_cy)
        pygame.draw.ellipse(surface, SHIRT_COLOUR, waist_rect)

        # 2. Belly skin
        belly_rect = pygame.Rect(0, 0, self.belly_rx * 2, self.belly_ry * 2)
        belly_rect.center = (self.belly_cx, self.belly_cy)
        pygame.draw.ellipse(surface, SKIN_COLOUR, belly_rect)

        # Belly art
        _draw_belly_art(surface, self.belly_cx, self.belly_cy, self.belly_rx, self.belly_ry)

        # 3. Moobs — shallow semi-ellipses drawn ON the lower visible belly
        #    Flat base faces down (toward screen bottom); dome rises toward toilet.
        #    Nipples sit at the apex of each dome.
        moob_hw = 56    # half-width per moob
        moob_h = 36     # dome height — shallow for a man's chest
        moob_sep = 8    # gap between the two moobs at the centre
        # Flat base at screen bottom edge — moobs are flush with bottom of screen
        flat_y = self.belly_cy + 4  # slightly off-screen so the flat line is hidden

        left_cx = self.belly_cx - moob_sep // 2 - moob_hw
        right_cx = self.belly_cx + moob_sep // 2 + moob_hw

        for cx in (left_cx, right_cx):
            _draw_semi_ellipse(surface, cx, flat_y, moob_hw, moob_h, MOOB_COLOUR)
            # Nipple at apex — the point of the dome closest to the toilet
            pygame.draw.circle(surface, NIPPLE_COLOUR, (cx, flat_y - moob_h), 5)
            pygame.draw.circle(surface, (145, 85, 65), (cx, flat_y - moob_h), 3)
            # A few hairs scattered on each moob surface
            _draw_moob_hair(surface, cx, flat_y, moob_h)

        # 4. Chest hair in the cleavage valley
        _draw_chest_hair(surface, self.belly_cx, flat_y - moob_h // 2)


def _draw_semi_ellipse(
    surface: pygame.Surface, cx: int, base_y: int, rx: int, ry: int, colour: tuple,
) -> None:
    """Fill the upper half of an ellipse. Flat base at base_y, dome curves upward."""
    # Sweep angles 0→180°; polygon auto-closes with the flat base line.
    points = [
        (int(cx + rx * math.cos(math.radians(a))),
         int(base_y - ry * math.sin(math.radians(a))))
        for a in range(0, 181)
    ]
    pygame.draw.polygon(surface, colour, points)


def _draw_belly_art(
    surface: pygame.Surface, cx: int, cy: int, rx: int, ry: int,
) -> None:
    """Draw belly button and stretch marks on the belly."""
    belly_button_colour = (180, 120, 95)
    stretch_colour = (210, 160, 130)

    # Belly button right at the top edge of the belly
    bb_y = cy - ry + 5
    stretch_colour = (220, 175, 148)  # very faint — barely visible

    # Short faint wrinkles radiating down from the button
    marks = [
        (-8,  2, -18,  8),
        ( 8,  2,  18,  8),
        (-14, 6, -28, 14),
        ( 14, 6,  28, 14),
        (  0, 8,   0, 20),
    ]
    for sx, sy, ex, ey in marks:
        pygame.draw.line(surface, stretch_colour, (cx + sx, bb_y + sy), (cx + ex, bb_y + ey), 1)

    # Belly button — innie dent at the edge
    pygame.draw.ellipse(surface, SKIN_SHADOW, (cx - 7, bb_y - 5, 14, 10))   # rim
    pygame.draw.ellipse(surface, belly_button_colour, (cx - 5, bb_y - 3, 10, 7))  # fold
    pygame.draw.ellipse(surface, (155, 100, 75), (cx - 3, bb_y - 2, 6, 4))  # dent


def _draw_moob_hair(
    surface: pygame.Surface, cx: int, base_y: int, moob_h: int,
) -> None:
    """Sparse hairs on the surface of one moob."""
    # Offsets relative to moob centre-x and a point mid-way up the dome
    mid_y = base_y - moob_h // 2
    hair_spots = [
        # (offset_x, offset_y, angle_deg, length)
        (-18, -4,  20, 7), ( 18, -4, -20, 7),
        ( -8, -12, -15, 6), (  8, -12,  15, 6),
        (  0, -18,  10, 7),
        (-22,  6,   30, 5), ( 22,  6,  -30, 5),
    ]
    for ox, oy, angle, length in hair_spots:
        x = cx + ox
        y = mid_y + oy
        rad = math.radians(angle)
        ex = x + math.cos(rad) * length
        ey = y + math.sin(rad) * length
        pygame.draw.line(surface, CHEST_HAIR, (x, y), (int(ex), int(ey)), 1)


def _draw_chest_hair(surface: pygame.Surface, cx: int, cy: int) -> None:
    """Short hairs in the cleavage valley and trailing down the belly."""
    hair_spots = [
        # Central cleavage valley
        ( 0, -6, -20, 8), ( 0,  2,  15, 7), ( 0, 10, -10, 9),
        (-5, -2,  30, 7), ( 5, -2, -30, 7),
        (-4, 14,  10, 8), ( 4, 14, -15, 8),
        # Trailing down the belly below the cleavage
        (-8, 30,  10, 7), ( 0, 32,  -5, 8), ( 8, 30, -12, 7),
        (-5, 44,  20, 6), ( 5, 44, -20, 6), ( 0, 48,   0, 7),
    ]
    for ox, oy, angle, length in hair_spots:
        x = cx + ox
        y = cy + oy
        rad = math.radians(angle)
        ex = x + math.cos(rad) * length
        ey = y + math.sin(rad) * length
        pygame.draw.line(surface, CHEST_HAIR, (x, y), (int(ex), int(ey)), 1)
