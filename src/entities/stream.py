"""Stream particle system — the pee stream."""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field

import pygame

from game.settings import (
    STREAM_COLOUR, STREAM_COLOUR_WEAK, STREAM_PARTICLE_RADIUS,
    STREAM_MAX_PARTICLES, STREAM_BASE_SPEED, STREAM_MIN_SPEED,
    STREAM_SPREAD, STREAM_EMIT_RATE, GRAVITY,
    SPLASH_COLOUR, SPLASH_PARTICLE_COUNT, SPLASH_PARTICLE_SPEED,
    SPLASH_PARTICLE_LIFETIME, SPLASH_PARTICLE_RADIUS,
)


@dataclass
class Particle:
    x: float
    y: float
    vx: float
    vy: float
    alive: bool = True
    in_bowl: bool = False  # debug: True when particle is inside the hitbox


@dataclass
class SplashParticle:
    x: float
    y: float
    vx: float
    vy: float
    lifetime: float
    colour: tuple[int, int, int] = field(default_factory=lambda: SPLASH_COLOUR)


class Stream:
    """Particle emitter for the pee stream."""

    def __init__(self, origin: tuple[float, float]) -> None:
        self.origin = origin
        self.particles: list[Particle] = []
        self.splashes: list[SplashParticle] = []
        self.emitting = True

    def emit(self, target_x: float, target_y: float, pressure: float) -> None:
        """Spawn new particles aimed at target, scaled by pressure."""
        if not self.emitting or pressure <= 0.0:
            return

        speed = STREAM_MIN_SPEED + (STREAM_BASE_SPEED - STREAM_MIN_SPEED) * pressure
        dx = target_x - self.origin[0]
        dy = target_y - self.origin[1]
        dist = math.hypot(dx, dy)
        if dist < 1.0:
            return

        base_angle = math.atan2(dy, dx)

        for _ in range(STREAM_EMIT_RATE):
            # Recycle oldest if at cap
            if len(self.particles) >= STREAM_MAX_PARTICLES:
                for p in self.particles:
                    if p.alive:
                        p.alive = False
                        break

            angle = base_angle + random.uniform(-STREAM_SPREAD, STREAM_SPREAD)
            p_speed = speed * random.uniform(0.9, 1.1)
            vx = math.cos(angle) * p_speed
            vy = math.sin(angle) * p_speed

            self.particles.append(Particle(
                x=self.origin[0], y=self.origin[1],
                vx=vx, vy=vy,
            ))

    def update(self, dt: float) -> None:
        """Move all particles. No gravity — stream travels in a straight line."""
        for p in self.particles:
            if not p.alive:
                continue
            p.x += p.vx * dt
            p.y += p.vy * dt

        # Update splash particles
        for s in self.splashes:
            s.x += s.vx * dt
            s.y += s.vy * dt
            s.lifetime -= dt

        # Clean up
        self.particles = [p for p in self.particles if p.alive]
        self.splashes = [s for s in self.splashes if s.lifetime > 0]

    def kill_particle(self, particle: Particle, spawn_splash: bool = True) -> None:
        """Kill a particle. Optionally spawn splash FX."""
        particle.alive = False
        if spawn_splash:
            self._spawn_splash(particle.x, particle.y)

    def _spawn_splash(self, x: float, y: float) -> None:
        """Create small splash particles at collision point."""
        for _ in range(SPLASH_PARTICLE_COUNT):
            angle = random.uniform(0, math.tau)
            speed = random.uniform(10, SPLASH_PARTICLE_SPEED)
            self.splashes.append(SplashParticle(
                x=x, y=y,
                vx=math.cos(angle) * speed,
                vy=math.sin(angle) * speed,
                lifetime=SPLASH_PARTICLE_LIFETIME,
            ))

    def draw(self, surface: pygame.Surface, pressure: float) -> None:
        """Draw all stream particles and splash effects."""
        colour = _lerp_colour(STREAM_COLOUR, STREAM_COLOUR_WEAK, 1.0 - pressure)

        for p in self.particles:
            if p.alive:
                p_colour = (255, 0, 0) if p.in_bowl else colour
                pygame.draw.circle(
                    surface, p_colour,
                    (int(p.x), int(p.y)),
                    STREAM_PARTICLE_RADIUS,
                )

        for s in self.splashes:
            alpha = max(0.0, s.lifetime / SPLASH_PARTICLE_LIFETIME)
            r = max(1, int(SPLASH_PARTICLE_RADIUS * (1.0 + alpha)))
            pygame.draw.circle(
                surface, s.colour,
                (int(s.x), int(s.y)), r,
            )


def _lerp_colour(c1: tuple, c2: tuple, t: float) -> tuple[int, int, int]:
    """Linear interpolation between two RGB colours."""
    t = max(0.0, min(1.0, t))
    return (
        int(c1[0] + (c2[0] - c1[0]) * t),
        int(c1[1] + (c2[1] - c1[1]) * t),
        int(c1[2] + (c2[2] - c1[2]) * t),
    )
