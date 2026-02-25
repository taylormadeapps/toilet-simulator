"""Stream physics orchestration."""

from entities.stream import Stream
from systems.bladder import Bladder
from systems.input_handler import get_pointer_position


def update_stream(stream: Stream, bladder: Bladder, dt: float) -> None:
    """Emit new particles toward pointer and advance all particles."""
    if not bladder.is_empty:
        target_x, target_y = get_pointer_position()
        stream.emit(target_x, target_y, bladder.pressure)
    else:
        stream.emitting = False

    stream.update(dt)
