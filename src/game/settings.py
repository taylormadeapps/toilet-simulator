"""Game-wide constants and configuration."""

from pathlib import Path

# Paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
ASSETS_DIR = PROJECT_ROOT / "assets"

# Display
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
WINDOW_TITLE = "Toilet Simulator"

# Colours (R, G, B)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 220, 50)
DARK_BLUE = (20, 25, 45)
LIGHT_BLUE = (100, 150, 220)
GOLD = (255, 200, 50)
GREY = (120, 120, 120)
