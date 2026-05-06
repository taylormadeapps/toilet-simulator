"""Game-wide constants and configuration."""

from pathlib import Path

import sys as _sys

# Paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
# Web (pygbag): the lll skill / CI stages everything (code + audio) into
# src/assets/, and pygbag cd's into that folder at runtime — so audio sits
# at the cwd, not at any absolute /assets path.
# Desktop: assets live alongside the repo root.
ASSETS_DIR = Path.cwd() if _sys.platform == "emscripten" else PROJECT_ROOT / "assets"

# Display — iPhone 14/15 logical resolution (portrait), scaled to 80% for desktop
SCREEN_WIDTH = 312
SCREEN_HEIGHT = 675
FPS = 60
WINDOW_TITLE = "Toilet Simulator"

# pygbag's pygame can't find "Arial" and falls back to a default font that
# renders larger at the same nominal point size. Shrink fonts on web so the
# UI matches the desktop layout.
FONT_SCALE = 0.75 if _sys.platform == "emscripten" else 1.0

# --- Colours (R, G, B) ---

# UI / general
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 220, 50)
DARK_BLUE = (20, 25, 45)
CENTRE_ZONE_COLOUR = (0, 200, 210)  # cyan target zone
LIGHT_BLUE = (100, 150, 220)
GOLD = (255, 200, 50)
GREY = (120, 120, 120)

# Player
SKIN_COLOUR = (235, 190, 150)
SKIN_SHADOW = (210, 165, 130)
SHIRT_COLOUR = (60, 80, 140)

# Stream
STREAM_COLOUR = (255, 230, 50)
STREAM_COLOUR_WEAK = (255, 240, 120)

# Toilet
BOWL_WHITE = (240, 240, 245)
BOWL_RIM = (200, 200, 210)
TOILET_BASE = (220, 220, 225)
WATER_COLOUR = (220, 230, 240)

# Floor
FLOOR_TILE_A = (180, 190, 185)
FLOOR_TILE_B = (165, 175, 170)
FLOOR_GROUT = (140, 145, 140)

# FX
SPLASH_COLOUR = (255, 255, 200)
PUDDLE_COLOUR = (255, 240, 100)

# HUD
HUD_BLADDER_FULL = (255, 220, 50)
HUD_BLADDER_EMPTY = (200, 80, 50)
HUD_TEXT = (255, 255, 255)
HUD_BG = (40, 40, 50)

# --- Physics ---
GRAVITY = 150.0
STREAM_BASE_SPEED = 500.0
STREAM_MIN_SPEED = 100.0
STREAM_SPREAD = 0.08
STREAM_EMIT_RATE = 3
STREAM_PARTICLE_RADIUS = 3
STREAM_MAX_PARTICLES = 1500
STREAM_DECEL = 340.0    # px/s² — constant deceleration simulating z-axis arc
STREAM_LAND_SPEED = 5.0   # px/s — speed threshold at which particle has landed

# --- Bladder ---
BLADDER_START = 1.0
BLADDER_DEPLETION_RATE = 0.055

# --- Scoring ---
SCORE_BOWL_HIT = 1       # points earned per drop in the bowl
SCORE_FLOOR_PENALTY = 1  # points lost per floor hit
SCORE_MIN = 0            # score floor

# --- Layout ---
BELLY_CENTRE_X = SCREEN_WIDTH // 2
BELLY_CENTRE_Y = SCREEN_HEIGHT
BELLY_RADIUS_X = 136
BELLY_RADIUS_Y = 104
STREAM_ORIGIN_X = SCREEN_WIDTH // 2
STREAM_ORIGIN_Y = BELLY_CENTRE_Y - BELLY_RADIUS_Y - 5

TOILET_CENTRE_X = SCREEN_WIDTH // 2
TOILET_CENTRE_Y = 200
BOWL_RADIUS_X = 64
BOWL_RADIUS_Y = 144

# --- Mouse pressure zone ---
PRESSURE_ZONE_TOP = 40       # mouse at top = max pressure
PRESSURE_ZONE_BOTTOM = 616   # mouse near belly = zero flow (much less sensitive)

# Aim sensitivity: scales how far the stream deflects from the virtual cursor.
# 1.0 = cursor position used directly; lower = narrower deflection range.
AIM_SENSITIVITY = 1.0

# Cursor speed: scales raw mouse delta applied to the virtual crosshair.
# 1.0 = 1:1 mouse movement; lower = slower, easier to aim precisely.
CURSOR_SPEED = 0.54

FLOOR_TILE_SIZE = 40

# --- Splash FX ---
SPLASH_PARTICLE_COUNT = 4
SPLASH_PARTICLE_SPEED = 60.0
SPLASH_PARTICLE_LIFETIME = 0.3
SPLASH_PARTICLE_RADIUS = 2
