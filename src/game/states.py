"""Game states — Splash, Playing, Results."""

from __future__ import annotations

import math
import random
from pathlib import Path
from typing import Optional

import pygame

from game.settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, DARK_BLUE, WHITE, GOLD, GREY, YELLOW, BLACK,
    FLOOR_TILE_A, FLOOR_TILE_B, FLOOR_GROUT, FLOOR_TILE_SIZE,
    PUDDLE_COLOUR,
    ASSETS_DIR, FONT_SCALE,
)


def _sysfont(name: str, size: int, bold: bool = False) -> pygame.font.Font:
    return pygame.font.SysFont(name, int(round(size * FONT_SCALE)), bold=bold)
from game.levels import PASS_STARS
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
    """Load a sound file and time-stretch it by factor (e.g. 1.25 = 20% slower).

    numpy is imported lazily here so module load doesn't fail on web before
    pygbag has had a chance to fetch the numpy wheel.
    """
    import numpy as np  # lazy: pygbag preloads numpy by the time this is called
    snd = pygame.mixer.Sound(str(path))
    arr = pygame.sndarray.array(snd).astype(np.float32)
    # arr shape: (num_samples,) mono or (num_samples, 2) stereo
    import numpy as np  # already imported lazily above; keep local refs concise
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
    """Title screen."""

    _SND_DIR = ASSETS_DIR / "sounds"
    _KNOCK_OFFSET = 2.0

    def __init__(self, level_manager=None) -> None:
        self.frame = 0
        self._lm = level_manager
        self._has_progress = level_manager is not None and level_manager._unlocked > 0
        self.font_title  = _sysfont("Arial", 48, bold=True)
        self.font_btn    = _sysfont("Arial", 20, bold=True)
        self.font_sub    = _sysfont("Arial", 15)
        self.title_top   = self.font_title.render("TOILET",    True, WHITE)
        self.title_bot   = self.font_title.render("SIMULATOR", True, GOLD)
        self.subtitle    = self.font_sub.render(
            "An irreverent PowerWash-alike", True, GREY,
        )
        self.transition: Optional[str] = None

        # Button layout
        cx = SCREEN_WIDTH // 2
        self._btn_play   = pygame.Rect(0, 0, 220, 46)
        self._btn_play.center = (cx, SCREEN_HEIGHT - 160 if self._has_progress else SCREEN_HEIGHT - 120)
        self._btn_select: Optional[pygame.Rect] = None
        if self._has_progress:
            self._btn_select = pygame.Rect(0, 0, 220, 46)
            self._btn_select.center = (cx, SCREEN_HEIGHT - 100)

        # Audio
        self._flush = pygame.mixer.Sound(str(self._SND_DIR / "flush.ogg"))
        self._knock = pygame.mixer.Sound(str(self._SND_DIR / "konck with sonny.ogg"))
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
                elif event.key == pygame.K_l and self._has_progress:
                    self._stop_sounds()
                    self.transition = "level_select"
                elif event.key == pygame.K_ESCAPE:
                    self._stop_sounds()
                    self.transition = "quit"
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos
                if self._btn_play.collidepoint(pos):
                    self._stop_sounds()
                    self.transition = "play"
                elif self._btn_select and self._btn_select.collidepoint(pos):
                    self._stop_sounds()
                    self.transition = "level_select"

    def update(self, dt: float) -> None:
        self.frame += 1
        self._elapsed += dt
        if not self._knock_played and self._elapsed >= self._knock_at:
            self._knock.play()
            self._knock_played = True

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(DARK_BLUE)
        cx = SCREEN_WIDTH // 2

        pulse = math.sin(self.frame * 0.05) * 0.08 + 1.0
        top_s = pygame.transform.rotozoom(self.title_top, 0, pulse)
        bot_s = pygame.transform.rotozoom(self.title_bot, 0, pulse)
        surface.blit(top_s, top_s.get_rect(centerx=cx, centery=SCREEN_HEIGHT // 3 - 20))
        surface.blit(bot_s, bot_s.get_rect(centerx=cx, centery=SCREEN_HEIGHT // 3 + 50))

        mouse = pygame.mouse.get_pos()

        # Play button
        hover_play = self._btn_play.collidepoint(mouse)
        pygame.draw.rect(surface, GOLD if hover_play else WHITE, self._btn_play, border_radius=8)
        lbl = self.font_btn.render("PLAY", True, DARK_BLUE)
        surface.blit(lbl, lbl.get_rect(center=self._btn_play.center))

        # Level select button
        if self._btn_select:
            hover_sel = self._btn_select.collidepoint(mouse)
            pygame.draw.rect(surface, GOLD if hover_sel else WHITE, self._btn_select, border_radius=8)
            lbl2 = self.font_btn.render("LEVEL SELECT", True, DARK_BLUE)
            surface.blit(lbl2, lbl2.get_rect(center=self._btn_select.center))

        surface.blit(self.subtitle, self.subtitle.get_rect(centerx=cx, centery=SCREEN_HEIGHT - 22))


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
        self.toilet = Toilet(level_config.get("bowl_scale", 1.0), level_config.get("toilet_offset_y", 0))
        self.stream = Stream(self.player.stream_origin)
        self.bladder = Bladder(
            level_config["bladder_volume"],
            level_config["depletion_rate"],
        )
        self._dark_mode: bool = level_config.get("dark_mode", False)
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
            ASSETS_DIR / "sounds" / "floor" / "weeeeee.ogg", factor=1.25
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
        if self._dark_mode:
            surface.fill((0, 0, 0))
        else:
            # 1. Floor
            _draw_floor(surface)
        # 2. Puddles (above floor, below toilet) — redraw only when changed
        if self._puddle_dirty:
            self._redraw_puddles()
        surface.blit(self._puddle_surf, (0, 0))
        if not self._dark_mode:
            # 3. Toilet
            self.toilet.draw(surface)
        # 4. Stream
        self.stream.draw(surface, self.bladder.pressure)
        if not self._dark_mode:
            # 5. Player belly (foreground)
            self.player.draw(surface)
        # 6. HUD (always on top)
        self.hud.draw(surface, self.bladder.volume, self.scoring.score, self._level_name)
        # 7. Targeting reticle over the hidden cursor
        _draw_reticle(surface)


# ---------------------------------------------------------------------------
# Results State
# ---------------------------------------------------------------------------

def _star_points(
    cx: float, cy: float, outer_r: float, inner_r: float
) -> list[tuple[float, float]]:
    pts = []
    for i in range(10):
        angle = math.radians(-90 + i * 36)
        r = outer_r if i % 2 == 0 else inner_r
        pts.append((cx + r * math.cos(angle), cy + r * math.sin(angle)))
    return pts


def _draw_star_row(
    surface: pygame.Surface,
    cx: int,
    cy: int,
    star_count: float,
    outer_r: int,
    color: tuple,
) -> None:
    """Draw 3 polygon stars (full / left-half / empty) centred at (cx, cy)."""
    inner_r = outer_r * 0.4
    spacing = int(outer_r * 2.6)
    full = int(star_count)
    has_half = (star_count - full) >= 0.25

    for i, sx in enumerate([cx - spacing, cx, cx + spacing]):
        pts = _star_points(sx, cy, outer_r, inner_r)
        if i < full:
            pygame.draw.polygon(surface, color, pts)
        elif i == full and has_half:
            # Left-half polygon: top→inner-upper-left→outer-left→inner-lower-left→outer-lower-left→bottom
            half_pts = [pts[0], pts[9], pts[8], pts[7], pts[6], pts[5]]
            pygame.draw.polygon(surface, color, half_pts)
            pygame.draw.polygon(surface, color, pts, 1)
        else:
            pygame.draw.polygon(surface, color, pts, 1)


# ---------------------------------------------------------------------------
# Level Select State
# ---------------------------------------------------------------------------

class LevelSelectState:
    """Level selection screen — accessible from the main menu."""

    _ROW_H   = 42
    _ROW_GAP = 10
    _PAD     = 16

    def __init__(self, level_manager) -> None:
        self.lm = level_manager
        self.font_title   = _sysfont("Arial", 26, bold=True)
        self.font_name    = _sysfont("Arial", 14)
        self.font_num     = _sysfont("Arial", 13)
        self.font_hint    = _sysfont("Arial", 13)
        self.font_confirm = _sysfont("Arial", 17, bold=True)
        self.transition: Optional[str] = None
        self._confirming = False
        self._rows, self._indices = self._build_rows()

        # Reset button — bottom left corner
        self._btn_reset = pygame.Rect(self._PAD, SCREEN_HEIGHT - 38, 100, 26)

        # Confirmation dialog buttons
        dialog_cx = SCREEN_WIDTH // 2
        self._btn_yes = pygame.Rect(0, 0, 90, 36)
        self._btn_yes.center = (dialog_cx - 54, SCREEN_HEIGHT // 2 + 30)
        self._btn_no  = pygame.Rect(0, 0, 90, 36)
        self._btn_no.center  = (dialog_cx + 54, SCREEN_HEIGHT // 2 + 30)

    def _build_rows(self) -> tuple[list[pygame.Rect], list[int]]:
        """Return (rects, level_indices) for only the unlocked levels."""
        rects, indices = [], []
        y = 60
        row_w = SCREEN_WIDTH - self._PAD * 2
        for i in range(self.lm.level_count):
            if self.lm.best_stars(i) == 0.0 and i != self.lm.current_level:
                break
            rects.append(pygame.Rect(self._PAD, y, row_w, self._ROW_H))
            indices.append(i)
            y += self._ROW_H + self._ROW_GAP
        return rects, indices

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self._confirming:
                        self._confirming = False
                    else:
                        self.transition = "splash"
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos
                if self._confirming:
                    if self._btn_yes.collidepoint(pos):
                        self.lm.reset()
                        self.transition = "splash"
                    elif self._btn_no.collidepoint(pos):
                        self._confirming = False
                else:
                    if self._btn_reset.collidepoint(pos):
                        self._confirming = True
                    else:
                        for rect, level_idx in zip(self._rows, self._indices):
                            if rect.collidepoint(pos):
                                self.lm.current_level = level_idx
                                self.transition = "play_level"
                                break

    def update(self, dt: float) -> None:
        pass

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(DARK_BLUE)
        cx = SCREEN_WIDTH // 2

        title = self.font_title.render("SELECT LEVEL", True, GOLD)
        surface.blit(title, title.get_rect(centerx=cx, y=14))

        mouse = pygame.mouse.get_pos()

        for rect, level_idx in zip(self._rows, self._indices):
            stars   = self.lm.best_stars(level_idx)
            hovered = rect.collidepoint(mouse)

            bg = (55, 65, 90) if hovered else (30, 38, 58)
            pygame.draw.rect(surface, bg, rect, border_radius=5)
            pygame.draw.rect(surface, GOLD if hovered else (70, 80, 100), rect, 1, border_radius=5)

            num_s  = self.font_num.render(f"{level_idx + 1:02d}", True, GREY)
            surface.blit(num_s, (rect.x + 8, rect.centery - num_s.get_height() // 2))

            cfg    = self.lm.config(level_idx)
            name_s = self.font_name.render(cfg["name"], True, WHITE)
            surface.blit(name_s, (rect.x + 32, rect.centery - name_s.get_height() // 2))

            star_color = GOLD if stars > 0 else (70, 80, 100)
            _draw_star_row(surface, rect.right - 38, rect.centery, stars, 6, star_color)

        hint = self.font_hint.render("ESC — back", True, GREY)
        surface.blit(hint, hint.get_rect(centerx=cx, y=SCREEN_HEIGHT - 22))

        # Reset button
        hover_reset = self._btn_reset.collidepoint(mouse) and not self._confirming
        pygame.draw.rect(surface, (80, 30, 30) if hover_reset else (50, 22, 22),
                         self._btn_reset, border_radius=4)
        pygame.draw.rect(surface, (160, 60, 60), self._btn_reset, 1, border_radius=4)
        rlbl = self.font_hint.render("Reset Save", True, (200, 80, 80))
        surface.blit(rlbl, rlbl.get_rect(center=self._btn_reset.center))

        # Confirmation overlay
        if self._confirming:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            surface.blit(overlay, (0, 0))

            box = pygame.Rect(24, SCREEN_HEIGHT // 2 - 55, SCREEN_WIDTH - 48, 110)
            pygame.draw.rect(surface, (28, 18, 18), box, border_radius=8)
            pygame.draw.rect(surface, (160, 60, 60), box, 2, border_radius=8)

            q1 = self.font_confirm.render("Reset all progress?", True, WHITE)
            q2 = self.font_hint.render("This cannot be undone.", True, (180, 100, 100))
            surface.blit(q1, q1.get_rect(centerx=cx, centery=SCREEN_HEIGHT // 2 - 24))
            surface.blit(q2, q2.get_rect(centerx=cx, centery=SCREEN_HEIGHT // 2 - 4))

            hover_yes = self._btn_yes.collidepoint(mouse)
            hover_no  = self._btn_no.collidepoint(mouse)
            pygame.draw.rect(surface, (160, 40, 40) if hover_yes else (100, 28, 28),
                             self._btn_yes, border_radius=6)
            pygame.draw.rect(surface, (40, 100, 40) if hover_no else (28, 60, 28),
                             self._btn_no,  border_radius=6)
            yes_lbl = self.font_confirm.render("YES", True, WHITE)
            no_lbl  = self.font_confirm.render("NO",  True, WHITE)
            surface.blit(yes_lbl, yes_lbl.get_rect(center=self._btn_yes.center))
            surface.blit(no_lbl,  no_lbl.get_rect(center=self._btn_no.center))


class ResultsState:
    """Level complete — show star rating and score breakdown."""

    _GREEN = (80, 200, 100)
    _RED   = (220, 70, 70)

    def __init__(self, results: dict) -> None:
        self.results = results
        self.font_large  = _sysfont("Arial", 34, bold=True)
        self.font_medium = _sysfont("Arial", 24)
        self.font_small  = _sysfont("Arial", 18)

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
                elif event.key == pygame.K_l:
                    self.transition = "level_select"
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
            lbl = self.font_small.render(label,     True, GREY)
            val = self.font_medium.render(value_str, True, WHITE)
            surface.blit(lbl, lbl.get_rect(centerx=cx, y=y))
            surface.blit(val, val.get_rect(centerx=cx, y=y + 20))
            _draw_star_row(surface, cx, y + 56, star_val, 10, GOLD)
            y += 95

        # Divider
        pygame.draw.line(surface, GREY, (40, y), (SCREEN_WIDTH - 40, y), 1)
        y += 12

        # Overall stars — big centrepiece
        overall_lbl = self.font_small.render("Overall", True, GREY)
        surface.blit(overall_lbl, overall_lbl.get_rect(centerx=cx, y=y))
        _draw_star_row(surface, cx, y + 36, r["overall_stars"], 14, GOLD)
        y += 88

        # Pass / fail indicator
        passed = r["overall_stars"] >= PASS_STARS
        if passed:
            verdict = self.font_medium.render("PASSED!", True, self._GREEN)
        else:
            n_stars = int(PASS_STARS)
            part1 = self.font_small.render("Need", True, self._RED)
            part2 = self.font_small.render(" overall to advance", True, self._RED)
            total_w = part1.get_width() + 14 * 2 + part2.get_width()
            x0 = cx - total_w // 2
            text_cy = y + part1.get_height() // 2
            surface.blit(part1, (x0, y))
            x0 += part1.get_width() + 2
            for _ in range(n_stars):
                pts = _star_points(x0 + 7, text_cy, 7, 7 * 0.4)
                pygame.draw.polygon(surface, self._RED, pts)
                x0 += 16
            surface.blit(part2, (x0, y))
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
                lines = ["SPACE — next level", "R — retry   L — levels   ESC — menu"]
            else:
                lines = ["SPACE / R — retry", "L — levels   ESC — menu"]
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
