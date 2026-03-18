"""Earn-up scoring system."""

from game.settings import SCORE_BOWL_HIT, SCORE_FLOOR_PENALTY, SCORE_MIN


class Scoring:
    """Start at 0. +1 per bowl hit, -1 per floor hit (floored at 0)."""

    def __init__(self) -> None:
        self.score: int = 0
        self.bowl_hits: int = 0
        self.floor_hits: int = 0
        self.centre_hits: int = 0

    def register_bowl_hit(self, is_centre: bool = False) -> None:
        """Particle landed in the bowl."""
        self.score += SCORE_BOWL_HIT
        self.bowl_hits += 1
        if is_centre:
            self.centre_hits += 1

    def register_floor_hit(self) -> None:
        """Particle hit the floor — deduct a point, never below zero."""
        self.score = max(SCORE_MIN, self.score - SCORE_FLOOR_PENALTY)
        self.floor_hits += 1

    def finalise(self) -> dict:
        """Compute end-of-level stats. Call once when the level ends."""
        total = self.bowl_hits + self.floor_hits
        accuracy = round(self.bowl_hits / total * 100) if total > 0 else 0
        return {
            "score": self.score,
            "accuracy": accuracy,
            "bowl_hits": self.bowl_hits,
            "floor_hits": self.floor_hits,
            "centre_hits": self.centre_hits,
        }
