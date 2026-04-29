"""Game states — Splash, Playing, Results."""

from __future__ import annotations

import math
import random
from pathlib import Path
from typing import Optional

import numpy as np
import pygame

from game.settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, DARK_BLUE, WHITE, GOLD, GREY, YELLOW, BLACK,
    FLOOR_TILE_A, FLOOR_TILE_B, FLOOR_GROUT, FLOOR_TILE_SIZE,
    PUDDLE_COLOUR,
    ASSETS_DIR,
)
from game.levels import stars_str, PASS_STARS
from entities.player import Player
from entities.toilet import Toilet
from entities.stream import Stream
from systems.bladder import Bladder
from systems.scoring import Scoring
from systems.physics import update_stream
from systems.collision import check_collisions
from ui.hud import HUD
from systems.input_handler import get_pointer_position
from systems.audio import PeeAudio, FloorAudio


def _stretch_sound(path: Path, factor: float) -> pygame.mixer.Sound:
    """Load a WAV and time-stretch it by factor (e.g. 1.25 = 20% slower)."""
    snd = pygame.mixer.Sound(str(path))
    arr = pygame.sndarray.array(snd).astype(np.float32)
    # arr shape: (num_samples,) mono or (num_samples, 2) stereo
    n_in = arr.shape[0]
    n_out = int(round(n_in * factor))
    x_in = np.arange(n_in, dtype=np.float32)
    x_out = np.linspace(0, n_in - 1, n_out, dtype=np.float32)
    if arr.ndim == 1:
        stretched = np.interp(x_out, x_in, arr)
    else:
        stretched = np.column_stack(
            [np.interp(x_out, x_in, arr[:, ch]) for ch in range(arr.shape[1])]
        )
    stretched = np.clip(stretched, np.iinfo(np.int16).min, np.iinfo(np.int16).max)
    return pygame.sndarray.make_sound(stretched.astype(np.int16))


# ---------------------------------------------------------------------------
# Splash State
# ---------------------------------------------------------------------------

class SplashState:
    """Title screen. Press SPACE or click to play."""

    _SND_DIR = ASSETS_DIR / "pee sounds"
    _KNOCK_OFFSET = 2.0  # seconds before flush end to trigger the knock

    def __init__(self) -> None:
        self.frame = 0
        self.font_title = pygame.font.SysFont("Arial", 48, bold=True)
        self.font_prompt = pygame.font.SysFont("Arial", 22)
        self.font_sub = pygame.font.SysFont("Arial", 15)
        # Pre-render title surfaces (don't create fonts in the loop)
        self.title_top = self.font_title.render("TOILET", True, WHITE)
        self.title_bot = self.font_title.render("SIMULATOR", True, GOLD)
        self.subtitle = self.font_sub.render(
            "An irreverent PowerWash-alike", True, GREY,
        )
        self.transition: Optional[str] = None

        # Audio — flush plays immediately; knock fires in the last 2s of flush
        self._flush = pygame.mixer.Sound(str(self._SND_DIR / "flush.wav"))
        self._knock = pygame.mixer.Sound(str(self._SND_DIR / "konck with sonny.wav"))
        self._elapsed = 0.0
        self._knock_played = False
        self._knock_at = self._flush.get_length() - self._KNOCK_OFFSET
        self._flush.play()

    def _stop_sounds(self) -> None:
        self._flush.stop()
        self._knock.stop()

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self._stop_sounds()
                    self.transition = "play"
                elif event.key == pygame.K_ESCAPE:
                    self._stop_sounds()
                    self.transition = "quit"
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self._stop_sounds()
                self.transition = "play"

    def update(self, dt: float) -> None:
        self.frame += 1
        self._elapsed += dt
        # Trigger knock in the last 2 seconds of the flush sample
        if not self._knock_played and self._elapsed >= self._knock_at:
            self._knock.play()
            self._knock_played = True

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
            prompt = self.font_prompt.render("Click or SPACE to start", True, YELLOW)
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

    _PEE_COOLDOWN = 1.0    # seconds before pee can flow at level start
    _MERGE_RADIUS = 30     # px — hits within this distance grow the nearest puddle
    _PUDDLE_START_R = 5    # px — radius of a brand-new puddle
    _PUDDLE_GROW = 0.4     # px added to radius per floor hit

    def __init__(self, level_config: dict) -> None:
        num = level_config.get("level_number", "")
        self._level_name = f"Level {num}: {level_config['name']}" if num else level_config["name"]
        self.player = Player()
        self.toilet = Toilet()
        self.stream = Stream(self.player.stream_origin)
        self.bladder = Bladder(
            level_config["bladder_volume"],
            level_config["depletion_rate"],
        )
        self.scoring = Scoring()
        self.hud = HUD()
        self.pee_audio = PeeAudio()
        self.floor_audio = FloorAudio()
        # List of [x, y, radius] puddles; grows as floor hits accumulate
        self._puddles: list[list[float]] = []
        self._puddle_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        self._puddle_dirty = False
        # Stretch to 1.25× length so it plays 20% slower
        self._weeee = _stretch_sound(
            ASSETS_DIR / "pee sounds" / "floor" / "weeeeee.wav", factor=1.25
        )
        self.transition: Optional[str] = None
        self.results_data: Optional[dict] = None
        self._cooldown = self._PEE_COOLDOWN

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.pee_audio.stop()
                    self.floor_audio.stop()
                    self.transition = "splash"

    def update(self, dt: float) -> None:
        # Hold off emission for the first second so the level has a moment to load
        if self._cooldown > 0.0:
            self._cooldown -= dt
            if self._cooldown <= 0.0:
                self._weeee.play()
            self.stream.update(dt)
            return

        # update_stream returns mouse pressure (0–1) used this tick
        flow = update_stream(self.stream, self.bladder, dt)
        # Bladder only depletes while actually flowing
        self.bladder.update(dt, flow_rate=flow)
        bowl_hits, centre_hits, floor_positions = check_collisions(self.stream, self.toilet, self.scoring)
        # Bowl audio: volume scales with hit count; centre hits unlock max volume
        self.pee_audio.update(dt, flow, bowl_hits=bowl_hits, centre_hits=centre_hits)
        # Floor audio: independently driven by floor hit count — blends with bowl audio
        self.floor_audio.update(dt, flow, floor_hits=len(floor_positions))
        # Paint a puddle splat for each floor landing
        for x, y in floor_positions:
            self._splat(x, y)

        # Level ends when bladder empty AND all particles have landed
        if self.bladder.is_empty and len(self.stream.particles) == 0:
            self.pee_audio.stop()
            self.floor_audio.stop()
            self.results_data = self.scoring.finalise()
            self.transition = "results"

    def _splat(self, x: float, y: float) -> None:
        """Grow the nearest puddle or start a new one, then mark as dirty."""
        best: list[float] | None = None
        best_dist = self._MERGE_RADIUS
        for p in self._puddles:
            d = math.hypot(x - p[0], y - p[1])
            if d < best_dist:
                best_dist = d
                best = p
        if best is not None:
            best[2] += self._PUDDLE_GROW
        else:
            self._puddles.append([x, y, float(self._PUDDLE_START_R)])
        self._puddle_dirty = True

    def _redraw_puddles(self) -> None:
        """Redraw all puddles onto the cached surface."""
        self._puddle_surf.fill((0, 0, 0, 0))
        for px, py, pr in self._puddles:
            rx = int(pr)
            ry = max(1, int(pr * 0.55))  # flattened ellipse for top-down look
            pygame.draw.ellipse(
                self._puddle_surf,
                (*PUDDLE_COLOUR, 160),
                (int(px) - rx, int(py) - ry, rx * 2, ry * 2),
            )
        self._puddle_dirty = False

    def draw(self, surface: pygame.Surface) -> None:
        # 1. Floor
        _draw_floor(surface)
        # 2. Puddles (above floor, below toilet) — redraw only when changed
        if self._puddle_dirty:
            self._redraw_puddles()
        surface.blit(self._puddle_surf, (0, 0))
        # 3. Toilet
        self.toilet.draw(surface)
        # 4. Stream
        self.stream.draw(surface, self.bladder.pressure)
        # 5. Player belly (foreground)
        self.player.draw(surface)
        # 6. HUD (always on top)
        self.hud.draw(surface, self.bladder.volume, self.scoring.score, self._level_name)
        # 7. Targeting reticle over the hidden cursor
        _draw_reticle(surface)


# ---------------------------------------------------------------------------
# Results State
# ---------------------------------------------------------------------------

class ResultsState:
    """Level complete — show star rating and score breakdown."""

    _GREEN = (80, 200, 100)
    _RED   = (220, 70, 70)

    def __init__(self, results: dict) -> None:
        self.results = results
        self.font_large  = pygame.font.SysFont("Arial", 34, bold=True)
        self.font_medium = pygame.font.SysFont("Arial", 24)
        self.font_small  = pygame.font.SysFont("Arial", 18)
        # Segoe UI Symbol has ★/☆ glyphs; fall back to DejaVu Sans
        self.font_stars_lg = pygame.font.SysFont("Segoe UI Symbol,DejaVu Sans", 34)
        self.font_stars_md = pygame.font.SysFont("Segoe UI Symbol,DejaVu Sans", 24)
        self.frame = 0
        self.transition: Optional[str] = None

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        r = self.results
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.transition = "next_level" if r.get("can_advance") else "retry"
                elif event.key == pygame.K_r:
                    self.transition = "retry"
                elif event.key == pygame.K_ESCAPE:
                    self.transition = "splash"
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.transition = "next_level" if r.get("can_advance") else "retry"

    def update(self, dt: float) -> None:
        self.frame += 1

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(DARK_BLUE)
        r = self.results
        cx = SCREEN_WIDTH // 2

        # Level number + name
        num  = r.get("level_number", "")
        raw  = r.get("level_name", "")
        label = f"Level {num}: {raw}" if num else raw
        name = self.font_small.render(label, True, GREY)
        surface.blit(name, name.get_rect(centerx=cx, y=18))

        # Title
        title = self.font_large.render("LEVEL COMPLETE", True, GOLD)
        surface.blit(title, title.get_rect(centerx=cx, y=45))

        # Star rows — score and accuracy
        y = 120
        for label, value_str, star_val in (
            ("Score",    str(r["score"]),          r["score_stars"]),
            ("Accuracy", f"{r['accuracy']}%",      r["acc_stars"]),
        ):
            lbl  = self.font_small.render(label,    True, GREY)
            val  = self.font_medium.render(value_str, True, WHITE)
            star = self.font_stars_md.render(stars_str(star_val), True, GOLD)
            surface.blit(lbl,  lbl.get_rect(centerx=cx, y=y))
            surface.blit(val,  val.get_rect(centerx=cx, y=y + 20))
            surface.blit(star, star.get_rect(centerx=cx, y=y + 46))
            y += 95

        # Divider
        pygame.draw.line(surface, GREY, (40, y), (SCREEN_WIDTH - 40, y), 1)
        y += 12

        # Overall stars — big centrepiece
        overall_lbl  = self.font_small.render("Overall", True, GREY)
        overall_star = self.font_stars_lg.render(stars_str(r["overall_stars"]), True, GOLD)
        surface.blit(overall_lbl,  overall_lbl.get_rect(centerx=cx, y=y))
        surface.blit(overall_star, overall_star.get_rect(centerx=cx, y=y + 22))
        y += 88

        # Pass / fail indicator
        passed = r["overall_stars"] >= PASS_STARS
        if passed:
            verdict = self.font_medium.render("PASSED!", True, self._GREEN)
        else:
            needed = self.font_stars_md.render(
                f"Need {PASS_STARS:.0f}\u2605 overall to advance", True, self._RED,
            )
            surface.blit(needed, needed.get_rect(centerx=cx, y=y))
            y += 28
            verdict = self.font_medium.render("Keep trying!", True, self._RED)
        surface.blit(verdict, verdict.get_rect(centerx=cx, y=y))
        y += 40

        # Small stats
        for line in (
            f"Bowl: {r['bowl_hits']}   Centre: {r['centre_hits']}",
            f"Floor hits: {r['floor_hits']}",
        ):
            t = self.font_small.render(line, True, GREY)
            surface.blit(t, t.get_rect(centerx=cx, y=y))
            y += 22

        # Blinking prompt
        if (self.frame // 30) % 2 == 0:
            if r.get("can_advance"):
                lines = ["SPACE — next level", "R — retry   ESC — menu"]
            else:
                lines = ["SPACE / R — retry", "ESC — menu"]
            py = SCREEN_HEIGHT - 60
            for line in lines:
                t = self.font_small.render(line, True, YELLOW)
                surface.blit(t, t.get_rect(centerx=cx, y=py))
                py += 24


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
