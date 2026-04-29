"""Level unlock tracking and persistent save/load."""

from __future__ import annotations

import json

from game.levels import LEVELS, PASS_STARS
from game.settings import PROJECT_ROOT

_SAVE_PATH = PROJECT_ROOT / "saves" / "progress.json"


class LevelManager:
    """Tracks which levels are unlocked and the best star rating per level."""

    def __init__(self) -> None:
        self.current_level: int = 0
        self._unlocked: int = 0          # highest unlocked index
        self._best_stars: list[float] = [0.0] * len(LEVELS)
        self._load()

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    @property
    def level_count(self) -> int:
        return len(LEVELS)

    def current_config(self) -> dict:
        return LEVELS[self.current_level]

    def is_unlocked(self, idx: int) -> bool:
        return idx <= self._unlocked

    def best_stars(self, idx: int) -> float:
        return self._best_stars[idx]

    def can_advance(self) -> bool:
        """True if the next level exists and is unlocked."""
        return self.current_level + 1 < len(LEVELS) and \
               self.current_level + 1 <= self._unlocked

    # ------------------------------------------------------------------
    # Mutations
    # ------------------------------------------------------------------

    def record_result(self, overall_stars: float) -> None:
        """Update best stars for the current level and unlock the next if passed."""
        idx = self.current_level
        if overall_stars > self._best_stars[idx]:
            self._best_stars[idx] = overall_stars
        if overall_stars >= PASS_STARS and idx + 1 < len(LEVELS):
            if idx + 1 > self._unlocked:
                self._unlocked = idx + 1
        self._save()

    def advance(self) -> None:
        """Move to the next level (caller should check can_advance first)."""
        if self.current_level + 1 < len(LEVELS):
            self.current_level += 1

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def _load(self) -> None:
        if not _SAVE_PATH.exists():
            return
        try:
            data = json.loads(_SAVE_PATH.read_text())
            self._unlocked = int(data.get("unlocked", 0))
            for i, s in enumerate(data.get("best_stars", [])[:len(LEVELS)]):
                self._best_stars[i] = float(s)
        except Exception:
            pass  # corrupt save — start fresh

    def _save(self) -> None:
        _SAVE_PATH.parent.mkdir(parents=True, exist_ok=True)
        _SAVE_PATH.write_text(json.dumps({
            "unlocked": self._unlocked,
            "best_stars": self._best_stars,
        }))
