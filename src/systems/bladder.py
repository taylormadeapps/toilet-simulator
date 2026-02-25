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

    def update(self, dt: float, flow_rate: float = 1.0) -> None:
        """Deplete bladder. flow_rate scales depletion (0 = paused)."""
        self.volume = max(0.0, self.volume - self.depletion_rate * flow_rate * dt)
