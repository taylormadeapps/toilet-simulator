"""Stream vs bowl/floor collision detection."""

import math

from entities.stream import Stream
from entities.toilet import Toilet
from systems.scoring import Scoring
from game.settings import SCREEN_WIDTH, SCREEN_HEIGHT, STREAM_LAND_SPEED


def check_collisions(
    stream: Stream, toilet: Toilet, scoring: Scoring,
) -> tuple[int, int, list[tuple[float, float]]]:
    """Score particles when they land.

    Returns (bowl_hits, centre_hits, floor_positions) this frame.
    floor_positions is a list of (x, y) landing coords for every floor hit
    so callers can render puddles at the exact landing spots.
    """
    bowl_hits = 0
    centre_hits = 0
    floor_positions: list[tuple[float, float]] = []
    for particle in stream.particles:
        if not particle.alive:
            continue

        # Off-screen — counts as a miss before landing
        if _is_off_screen(particle.x, particle.y):
            scoring.register_floor_hit()
            stream.kill_particle(particle, spawn_splash=False)
            # Clamp off-screen hits to the nearest edge so the splat stays visible
            cx = max(0.0, min(particle.x, SCREEN_WIDTH))
            cy = max(0.0, min(particle.y, SCREEN_HEIGHT))
            floor_positions.append((cx, cy))
            continue

        # Particle has landed when speed reaches ~zero
        if math.hypot(particle.vx, particle.vy) <= STREAM_LAND_SPEED:
            if toilet.is_in_bowl(particle.x, particle.y):
                is_centre = toilet.is_in_centre(particle.x, particle.y)
                scoring.register_bowl_hit(is_centre=is_centre)
                stream.kill_particle(particle, spawn_splash=True)
                if is_centre:
                    centre_hits += 1
                else:
                    bowl_hits += 1
            else:
                scoring.register_floor_hit()
                stream.kill_particle(particle, spawn_splash=False)
                floor_positions.append((particle.x, particle.y))
    return bowl_hits, centre_hits, floor_positions


def _is_off_screen(x: float, y: float) -> bool:
    """Check if a particle has left the screen in any direction."""
    return x < -20 or x > SCREEN_WIDTH + 20 or y < -20 or y > SCREEN_HEIGHT + 20
