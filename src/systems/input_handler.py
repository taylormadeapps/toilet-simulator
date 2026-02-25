"""Pointer input abstraction. Mouse now, touch later."""

import pygame


def get_pointer_position() -> tuple[int, int]:
    """Return current pointer position in screen-space pixels."""
    return pygame.mouse.get_pos()
