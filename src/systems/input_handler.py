"""Pointer input abstraction. Mouse now, touch later.

A virtual cursor accumulates scaled relative mouse movement so the crosshair
moves slower than the physical mouse — easier to aim precisely.
"""

import pygame

from game.settings import SCREEN_WIDTH, SCREEN_HEIGHT, CURSOR_SPEED

# Virtual cursor position — starts at screen centre.
_vx: float = SCREEN_WIDTH / 2.0
_vy: float = SCREEN_HEIGHT / 2.0


def update_cursor() -> None:
    """Apply scaled relative mouse delta to the virtual cursor each frame."""
    global _vx, _vy
    dx, dy = pygame.mouse.get_rel()
    _vx = max(0.0, min(float(SCREEN_WIDTH), _vx + dx * CURSOR_SPEED))
    _vy = max(0.0, min(float(SCREEN_HEIGHT), _vy + dy * CURSOR_SPEED))


def reset_cursor() -> None:
    """Re-centre the virtual cursor — call when entering play state."""
    global _vx, _vy
    _vx = SCREEN_WIDTH / 2.0
    _vy = SCREEN_HEIGHT / 2.0
    pygame.mouse.get_rel()  # flush any accumulated delta


def get_pointer_position() -> tuple[float, float]:
    """Return current virtual cursor position in screen-space pixels."""
    return _vx, _vy
