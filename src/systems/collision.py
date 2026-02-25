"""Stream vs bowl/floor collision detection."""

from entities.stream import Stream
from entities.toilet import Toilet
from systems.scoring import Scoring
from game.settings import SCREEN_WIDTH, SCREEN_HEIGHT


def check_collisions(stream: Stream, toilet: Toilet, scoring: Scoring) -> None:
    """Test each alive particle for bowl or floor collision."""
    for particle in stream.particles:
        if not particle.alive:
            continue

        # Skip particles still above the bowl zone (mid-arc)
        if particle.y < toilet.centre_y - toilet.bowl_ry - 10:
            continue

        if toilet.is_in_bowl(particle.x, particle.y):
            # Hit the bowl — good
            is_centre = toilet.is_in_centre(particle.x, particle.y)
            scoring.register_bowl_hit(is_centre=is_centre)
            stream.kill_particle(particle, spawn_splash=True)

        elif _is_off_screen(particle.x, particle.y):
            # Off screen — kill silently
            particle.alive = False

        else:
            # Hit the floor — bad
            scoring.register_floor_hit()
            stream.kill_particle(particle, spawn_splash=True)


def _is_off_screen(x: float, y: float) -> bool:
    """Check if a particle has left the screen bounds."""
    return x < -20 or x > SCREEN_WIDTH + 20 or y < -20 or y > SCREEN_HEIGHT + 20
