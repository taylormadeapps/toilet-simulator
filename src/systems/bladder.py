"""Bladder volume, depletion, and pressure output."""


class Bladder:
    """Tracks bladder volume. Acts as the level timer."""

    def __init__(self, volume: float, depletion_rate: float) -> None:
        self.volume = volume
        self.depletion_rate = depletion_rate

    @property
    def pressure(self) -> float:
        """Current stream pressure. Equal to volume (1.0=full, 0.0=empty)."""
        return self.volume

    @property
    def is_empty(self) -> bool:
        return self.volume <= 0.0

    def update(self, dt: float) -> None:
        """Deplete bladder by dt seconds."""
        self.volume = max(0.0, self.volume - self.depletion_rate * dt)
