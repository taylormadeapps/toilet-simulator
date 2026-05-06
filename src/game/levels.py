"""Level definitions and global star-rating logic."""

from __future__ import annotations

import math

from game.settings import BLADDER_START, BLADDER_DEPLETION_RATE

# ---------------------------------------------------------------------------
# Global star thresholds — applied to every level
# ---------------------------------------------------------------------------

# (minimum value, stars awarded) — evaluated top-to-bottom, first match wins
_ACC_THRESHOLDS: list[tuple[float, float]] = [
    (90, 3.0), (80, 2.5), (70, 2.0), (55, 1.5), (40, 1.0), (20, 0.5),
]
_SCORE_THRESHOLDS: list[tuple[float, float]] = [
    (2500, 3.0), (2000, 2.5), (1500, 2.0), (1000, 1.5), (500, 1.0), (250, 0.5),
]

# Minimum overall stars required to unlock the next level
PASS_STARS = 2.0

# ---------------------------------------------------------------------------
# Level catalogue — all identical for now; layouts added level by level
# ---------------------------------------------------------------------------

LEVELS: list[dict] = [
    {"name": "The Porcelain Throne",     "bladder_volume": BLADDER_START, "depletion_rate": BLADDER_DEPLETION_RATE},
    {"name": "The Thimble",              "bladder_volume": BLADDER_START, "depletion_rate": BLADDER_DEPLETION_RATE, "bowl_scale": 0.625, "toilet_offset_y": 80},
    {"name": "Lights Out",               "bladder_volume": BLADDER_START, "depletion_rate": BLADDER_DEPLETION_RATE, "dark_mode": True},
    {"name": "Aim & Shame",              "bladder_volume": BLADDER_START, "depletion_rate": BLADDER_DEPLETION_RATE},
    {"name": "Wee Man Standing",         "bladder_volume": BLADDER_START, "depletion_rate": BLADDER_DEPLETION_RATE},
    {"name": "The Royal Flush",          "bladder_volume": BLADDER_START, "depletion_rate": BLADDER_DEPLETION_RATE},
    {"name": "Piddle Puddle Palace",     "bladder_volume": BLADDER_START, "depletion_rate": BLADDER_DEPLETION_RATE},
    {"name": "The Golden Gate",          "bladder_volume": BLADDER_START, "depletion_rate": BLADDER_DEPLETION_RATE},
    {"name": "Stream of Consciousness",  "bladder_volume": BLADDER_START, "depletion_rate": BLADDER_DEPLETION_RATE},
    {"name": "The Final Frontier",       "bladder_volume": BLADDER_START, "depletion_rate": BLADDER_DEPLETION_RATE},
]

# ---------------------------------------------------------------------------
# Star computation
# ---------------------------------------------------------------------------

def _threshold_stars(value: float, thresholds: list[tuple[float, float]]) -> float:
    for minimum, stars in thresholds:
        if value >= minimum:
            return stars
    return 0.0


def compute_stars(accuracy_pct: float, score: int) -> tuple[float, float, float]:
    """Return (acc_stars, score_stars, overall_stars), all in 0–3 half-star steps.

    Overall is the average of the two, rounded UP to the nearest 0.5.
    """
    acc_stars = _threshold_stars(accuracy_pct, _ACC_THRESHOLDS)
    score_stars = _threshold_stars(float(score), _SCORE_THRESHOLDS)
    raw_overall = (acc_stars + score_stars) / 2.0
    overall = math.ceil(raw_overall * 2) / 2   # round up to nearest 0.5
    return acc_stars, score_stars, overall


def stars_str(n: float) -> str:
    """Format a star count as a unicode string, e.g. 2.5 → '★★½☆'."""
    full = int(n)
    has_half = (n - full) >= 0.25
    empty = 3 - full - (1 if has_half else 0)
    return "★" * full + ("½" if has_half else "") + "☆" * empty
