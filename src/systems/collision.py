"""Stream vs bowl/floor collision detection."""

import math

from entities.stream import Stream
from entities.toilet import Toilet
from systems.scoring import Scoring
from game.settings import SCREEN_WIDTH, SCREEN_HEIGHT, STREAM_LAND_SPEED


def check_collisions(stream: Stream, toilet: Toilet, scoring: Scoring) -> None:
    """Score particles when they land (decelerate to ~zero speed).

    Particles follow a decelerating arc simulating the z-axis. When speed
    drops to near-zero the particle has landed — score based on position.
    """
    for particle in stream.particles:
        if not particle.alive:
            continue

        # Off-screen — counts as a miss before landing
        if _is_off_screen(particle.x, particle.y):
            scoring.register_floor_hit()
            stream.kill_particle(particle, spawn_splash=False)
            continue

        # Particle has landed when speed reaches ~zero
        if math.hypot(particle.vx, particle.vy) <= STREAM_LAND_SPEED:
            if toilet.is_in_bowl(particle.x, particle.y):
                is_centre = toilet.is_in_centre(particle.x, particle.y)
                scoring.register_bowl_hit(is_centre=is_centre)
                stream.kill_particle(particle, spawn_splash=True)
            else:
                scoring.register_floor_hit()
                stream.kill_particle(particle, spawn_splash=False)


def _is_off_screen(x: float, y: float) -> bool:
    """Check if a particle has left the screen in any direction."""
    return x < -20 or x > SCREEN_WIDTH + 20 or y < -20 or y > SCREEN_HEIGHT + 20
