"""Stream vs bowl/floor collision detection."""

from entities.stream import Stream
from entities.toilet import Toilet
from systems.scoring import Scoring
from game.settings import SCREEN_WIDTH, SCREEN_HEIGHT


def check_collisions(stream: Stream, toilet: Toilet, scoring: Scoring) -> None:
    """Test each alive particle for bowl hit or miss.

    No gravity — particles travel in straight lines. A particle either enters
    the bowl ellipse (score) or leaves the screen (miss).
    """
    for particle in stream.particles:
        if not particle.alive:
            continue

        # Off-screen in any direction — counts as a miss
        if _is_off_screen(particle.x, particle.y):
            scoring.register_floor_hit()
            stream.kill_particle(particle, spawn_splash=False)
            continue

        # Debug: highlight particle while inside the outer bowl visual
        particle.in_bowl = toilet.is_in_bowl(particle.x, particle.y)

        # Score only when the particle reaches the water zone at the bowl centre.
        # The outer bowl is visual-only — particles fly through it freely.
        if toilet.is_in_centre(particle.x, particle.y):
            scoring.register_bowl_hit(is_centre=True)
            stream.kill_particle(particle, spawn_splash=True)


def _is_off_screen(x: float, y: float) -> bool:
    """Check if a particle has left the screen in any direction."""
    return x < -20 or x > SCREEN_WIDTH + 20 or y < -20 or y > SCREEN_HEIGHT + 20
