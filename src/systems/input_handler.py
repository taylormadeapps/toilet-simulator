"""Pointer input abstraction. Mouse now, touch later.

A virtual cursor accumulates scaled relative mouse movement so the crosshair
moves slower than the physical mouse — easier to aim precisely.

On web (emscripten), pointer-lock isn't reliable, so we fall back to
absolute mouse position — the reticle simply tracks the OS cursor.
"""

from __future__ import annotations

import sys

import pygame

from game.settings import SCREEN_WIDTH, SCREEN_HEIGHT, CURSOR_SPEED

_IS_WEB = sys.platform == "emscripten"

# Virtual cursor position — starts at screen centre.
_vx: float = SCREEN_WIDTH / 2.0
_vy: float = SCREEN_HEIGHT / 2.0


def update_cursor() -> None:
    """Update the virtual cursor each frame.

    Desktop: scaled relative mouse delta (precision aiming).
    Web: absolute mouse position (pointer lock not reliable in browser).
    """
    global _vx, _vy
    if _IS_WEB:
        x, y = pygame.mouse.get_pos()
        _vx = float(x)
        _vy = float(y)
    else:
        dx, dy = pygame.mouse.get_rel()
        _vx = max(0.0, min(float(SCREEN_WIDTH), _vx + dx * CURSOR_SPEED))
        _vy = max(0.0, min(float(SCREEN_HEIGHT), _vy + dy * CURSOR_SPEED))


def reset_cursor() -> None:
    """Re-centre the virtual cursor — call when entering play state."""
    global _vx, _vy
    if _IS_WEB:
        x, y = pygame.mouse.get_pos()
        _vx = float(x)
        _vy = float(y)
    else:
        _vx = SCREEN_WIDTH / 2.0
        _vy = SCREEN_HEIGHT / 2.0
        pygame.mouse.get_rel()  # flush any accumulated delta


def get_pointer_position() -> tuple[float, float]:
    """Return current virtual cursor position in screen-space pixels."""
    return _vx, _vy
