"""Penalty-based scoring system."""


class Scoring:
    """Start at max score, lose points for floor hits."""

    def __init__(self, start_score: int, floor_penalty: int,
                 centre_bonus: int, clean_bonus: int, min_score: int) -> None:
        self.score = start_score
        self.floor_penalty = floor_penalty
        self.centre_bonus = centre_bonus
        self.clean_bonus = clean_bonus
        self.min_score = min_score
        self.floor_hits = 0
        self.bowl_hits = 0
        self.centre_hits = 0

    def register_floor_hit(self) -> None:
        """Particle hit the floor. Apply penalty."""
        self.floor_hits += 1
        self.score = max(self.min_score, self.score - self.floor_penalty)

    def register_bowl_hit(self, is_centre: bool = False) -> None:
        """Particle hit the bowl. Optional centre bonus."""
        self.bowl_hits += 1
        if is_centre:
            self.centre_hits += 1
            self.score = min(self.score + self.centre_bonus, 9999)

    def finalise(self) -> dict:
        """Calculate final score with bonuses. Call at level end."""
        final = self.score
        clean = self.floor_hits == 0
        if clean:
            final += self.clean_bonus
        total_particles = self.floor_hits + self.bowl_hits
        accuracy = (self.bowl_hits / total_particles * 100) if total_particles > 0 else 0
        return {
            "score": final,
            "floor_hits": self.floor_hits,
            "bowl_hits": self.bowl_hits,
            "centre_hits": self.centre_hits,
            "accuracy": accuracy,
            "clean_finish": clean,
        }
