"""Stream physics orchestration — mouse-Y controls pressure."""

from entities.stream import Stream
from systems.bladder import Bladder
from systems.input_handler import get_pointer_position
from game.settings import (
    PRESSURE_ZONE_TOP, PRESSURE_ZONE_BOTTOM,
    STREAM_ORIGIN_X, STREAM_ORIGIN_Y, AIM_SENSITIVITY,
)


def mouse_pressure(mouse_y: float) -> float:
    """Map mouse Y to 0.0–1.0 pressure. Higher on screen = more pressure."""
    if mouse_y >= PRESSURE_ZONE_BOTTOM:
        return 0.0
    if mouse_y <= PRESSURE_ZONE_TOP:
        return 1.0
    return 1.0 - (mouse_y - PRESSURE_ZONE_TOP) / (PRESSURE_ZONE_BOTTOM - PRESSURE_ZONE_TOP)


def update_stream(stream: Stream, bladder: Bladder, dt: float) -> float:
    """Emit particles toward pointer, scaled by mouse-Y pressure.

    Returns the effective pressure (0.0–1.0) used this tick so callers
    can feed it to bladder depletion and HUD colour.
    """
    if bladder.is_empty:
        stream.emitting = False
        stream.update(dt)          # let remaining particles finish their arcs
        return 0.0

    mouse_x, mouse_y = get_pointer_position()
    m_pres = mouse_pressure(mouse_y)

    if m_pres <= 0.0:
        stream.emitting = False
        stream.update(dt)
        return 0.0

    # Scale aim offset from origin by sensitivity — less than 1.0 narrows the
    # deflection range so small mouse movements don't whip the stream around.
    target_x = STREAM_ORIGIN_X + (mouse_x - STREAM_ORIGIN_X) * AIM_SENSITIVITY
    target_y = STREAM_ORIGIN_Y + (mouse_y - STREAM_ORIGIN_Y) * AIM_SENSITIVITY

    # Re-enable emitting (may have been paused by a previous low-mouse tick)
    stream.emitting = True
    stream.emit(target_x, target_y, m_pres)
    stream.update(dt)
    return m_pres
