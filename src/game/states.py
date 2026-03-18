"""Game states — Splash, Playing, Results."""

from __future__ import annotations

import math
from typing import Optional

import pygame

from game.settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, DARK_BLUE, WHITE, GOLD, GREY, YELLOW, BLACK,
    BLADDER_START, BLADDER_DEPLETION_RATE,
    FLOOR_TILE_A, FLOOR_TILE_B, FLOOR_GROUT, FLOOR_TILE_SIZE,
)
from entities.player import Player
from entities.toilet import Toilet
from entities.stream import Stream
from systems.bladder import Bladder
from systems.scoring import Scoring
from systems.physics import update_stream
from systems.collision import check_collisions
from ui.hud import HUD
from systems.input_handler import get_pointer_position


# ---------------------------------------------------------------------------
# Splash State
# ---------------------------------------------------------------------------

class SplashState:
    """Title screen. Press SPACE or click to play."""

    def __init__(self) -> None:
        self.frame = 0
        self.font_title = pygame.font.SysFont("Arial", 64, bold=True)
        self.font_prompt = pygame.font.SysFont("Arial", 28)
        self.font_sub = pygame.font.SysFont("Arial", 16)
        # Pre-render title surfaces (don't create fonts in the loop)
        self.title_top = self.font_title.render("TOILET", True, WHITE)
        self.title_bot = self.font_title.render("SIMULATOR", True, GOLD)
        self.subtitle = self.font_sub.render(
            "An irreverent take on PowerWash Simulator", True, GREY,
        )
        self.transition: Optional[str] = None

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.transition = "play"
                elif event.key == pygame.K_ESCAPE:
                    self.transition = "quit"
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.transition = "play"

    def update(self, dt: float) -> None:
        self.frame += 1

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(DARK_BLUE)

        # Pulsing scale via transform (no per-frame font creation)
        pulse = math.sin(self.frame * 0.05) * 0.08 + 1.0
        top_scaled = pygame.transform.rotozoom(self.title_top, 0, pulse)
        bot_scaled = pygame.transform.rotozoom(self.title_bot, 0, pulse)

        surface.blit(top_scaled, top_scaled.get_rect(
            centerx=SCREEN_WIDTH // 2, centery=SCREEN_HEIGHT // 3 - 20))
        surface.blit(bot_scaled, bot_scaled.get_rect(
            centerx=SCREEN_WIDTH // 2, centery=SCREEN_HEIGHT // 3 + 50))

        # Blinking prompt
        if (self.frame // 30) % 2 == 0:
            prompt = self.font_prompt.render("Click or press SPACE to start", True, YELLOW)
            surface.blit(prompt, prompt.get_rect(
                centerx=SCREEN_WIDTH // 2, centery=SCREEN_HEIGHT - 100))

        # Subtitle
        surface.blit(self.subtitle, self.subtitle.get_rect(
            centerx=SCREEN_WIDTH // 2, centery=SCREEN_HEIGHT - 50))


# ---------------------------------------------------------------------------
# Playing State
# ---------------------------------------------------------------------------

class PlayingState:
    """Active gameplay — Level 1."""

    def __init__(self) -> None:
        self.player = Player()
        self.toilet = Toilet()
        self.stream = Stream(self.player.stream_origin)
        self.bladder = Bladder(BLADDER_START, BLADDER_DEPLETION_RATE)
        self.scoring = Scoring()
        self.hud = HUD()
        self.transition: Optional[str] = None
        self.results_data: Optional[dict] = None

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.transition = "splash"

    def update(self, dt: float) -> None:
        # update_stream returns mouse pressure (0–1) used this tick
        flow = update_stream(self.stream, self.bladder, dt)
        # Bladder only depletes while actually flowing
        self.bladder.update(dt, flow_rate=flow)
        check_collisions(self.stream, self.toilet, self.scoring)

        # Level ends when bladder empty AND all particles have landed
        if self.bladder.is_empty and len(self.stream.particles) == 0:
            self.results_data = self.scoring.finalise()
            self.transition = "results"

    def draw(self, surface: pygame.Surface) -> None:
        # 1. Floor
        _draw_floor(surface)
        # 2. Toilet
        self.toilet.draw(surface)
        # 3. Stream
        self.stream.draw(surface, self.bladder.pressure)
        # 4. Player belly (foreground)
        self.player.draw(surface)
        # 5. HUD (always on top)
        self.hud.draw(surface, self.bladder.volume, self.scoring.score)
        # 6. Targeting reticle over the hidden cursor
        _draw_reticle(surface)


# ---------------------------------------------------------------------------
# Results State
# ---------------------------------------------------------------------------

class ResultsState:
    """Level complete — show score breakdown."""

    def __init__(self, results: dict) -> None:
        self.results = results
        self.font_large = pygame.font.SysFont("Arial", 48, bold=True)
        self.font_medium = pygame.font.SysFont("Arial", 28)
        self.font_small = pygame.font.SysFont("Arial", 22)
        self.frame = 0
        self.transition: Optional[str] = None

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.transition = "splash"
                elif event.key == pygame.K_ESCAPE:
                    self.transition = "quit"
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.transition = "splash"

    def update(self, dt: float) -> None:
        self.frame += 1

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(DARK_BLUE)
        r = self.results

        # Title
        title = self.font_large.render("LEVEL COMPLETE", True, GOLD)
        surface.blit(title, title.get_rect(centerx=SCREEN_WIDTH // 2, y=60))

        # Big score
        score_text = self.font_large.render(f"{r['score']}", True, WHITE)
        surface.blit(score_text, score_text.get_rect(
            centerx=SCREEN_WIDTH // 2, y=140))

        # Stats
        y = 230
        stats = [
            f"Accuracy:     {r['accuracy']}%",
            f"Bowl hits:    {r['bowl_hits']}",
            f"Centre hits:  {r['centre_hits']}",
            f"Floor hits:   {r['floor_hits']}",
        ]

        for line in stats:
            text = self.font_medium.render(line, True, WHITE)
            surface.blit(text, text.get_rect(centerx=SCREEN_WIDTH // 2, y=y))
            y += 40

        # Blinking prompt
        if (self.frame // 30) % 2 == 0:
            prompt = self.font_small.render("Click or press SPACE to continue", True, YELLOW)
            surface.blit(prompt, prompt.get_rect(
                centerx=SCREEN_WIDTH // 2, y=SCREEN_HEIGHT - 80))


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _draw_floor(surface: pygame.Surface) -> None:
    """Draw a checkerboard bathroom floor."""
    for row in range(SCREEN_HEIGHT // FLOOR_TILE_SIZE + 1):
        for col in range(SCREEN_WIDTH // FLOOR_TILE_SIZE + 1):
            x = col * FLOOR_TILE_SIZE
            y = row * FLOOR_TILE_SIZE
            colour = FLOOR_TILE_A if (row + col) % 2 == 0 else FLOOR_TILE_B
            pygame.draw.rect(surface, colour,
                             (x, y, FLOOR_TILE_SIZE, FLOOR_TILE_SIZE))
            pygame.draw.rect(surface, FLOOR_GROUT,
                             (x, y, FLOOR_TILE_SIZE, FLOOR_TILE_SIZE), 1)


def _draw_reticle(surface: pygame.Surface) -> None:
    """Draw a crosshair at the virtual cursor position."""
    x, y = (int(v) for v in get_pointer_position())
    r = 10   # radius of gap in centre
    arm = 6  # length of each arm beyond the gap
    colour = (255, 255, 255)
    shadow = (0, 0, 0)

    lines = [
        ((x - r - arm, y), (x - r, y)),       # left arm
        ((x + r, y), (x + r + arm, y)),         # right arm
        ((x, y - r - arm), (x, y - r)),         # top arm
        ((x, y + r), (x, y + r + arm)),         # bottom arm
    ]
    for start, end in lines:
        pygame.draw.line(surface, shadow, (start[0]+1, start[1]+1),
                         (end[0]+1, end[1]+1), 2)
        pygame.draw.line(surface, colour, start, end, 2)
    pygame.draw.circle(surface, shadow, (x + 1, y + 1), r, 1)
    pygame.draw.circle(surface, colour, (x, y), r, 1)
