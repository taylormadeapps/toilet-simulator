"""Stream vs bowl/floor collision detection."""

from entities.stream import Stream
from entities.toilet import Toilet
from systems.scoring import Scoring
from game.settings import SCREEN_WIDTH, SCREEN_HEIGHT


def check_collisions(stream: Stream, toilet: Toilet, scoring: Scoring) -> None:
    """Test each alive particle for bowl or floor collision.

    Only checks particles that are descending (vy > 0). On the way up
    the stream flies freely — the bowl hitbox is for scoring, not a wall.
    Floor hits only register once the particle has fallen past the bowl.
    """
    # Floor threshold: below the bowl bottom, the particle clearly missed
    floor_y = toilet.centre_y + toilet.bowl_ry + 10

    for particle in stream.particles:
        if not particle.alive:
            continue

        # Off-screen — kill silently regardless of direction
        if _is_off_screen(particle.x, particle.y):
            particle.alive = False
            continue

        # Only score/kill particles that are falling back down
        if particle.vy <= 0:
            continue

        if toilet.is_in_bowl(particle.x, particle.y):
            # Landed in the bowl — good
            is_centre = toilet.is_in_centre(particle.x, particle.y)
            scoring.register_bowl_hit(is_centre=is_centre)
            stream.kill_particle(particle, spawn_splash=True)

        elif particle.y > floor_y:
            # Fallen past the bowl — floor hit
            scoring.register_floor_hit()
            stream.kill_particle(particle, spawn_splash=True)


def _is_off_screen(x: float, y: float) -> bool:
    """Check if a particle has left the screen bounds."""
    return x < -20 or x > SCREEN_WIDTH + 20 or y < -20 or y > SCREEN_HEIGHT + 20
