"""Toilet Simulator — Entry Point."""

# /// script
# dependencies = [
#     "pygame-ce",
#     "numpy",
# ]
# ///
# ^ PEP 723 inline dependencies — tells pygbag to fully preload these wheels
# before running this script. Without this, pygbag lazy-loads C extensions
# and our `import pygame` returns a stub missing pygame.init / pygame.Surface
# until the event loop has spun a few times. Ignored on desktop.

import asyncio
import sys


def _probe(msg: str) -> None:
    """Log to browser DevTools console (and stdout). Cheap, robust."""
    try:
        import js as _js  # type: ignore[import]
        _js.console.log(msg)
    except Exception:
        pass
    try:
        print(msg, flush=True)
    except Exception:
        pass


_probe("[toiletsim] L1 module top, about to import Game")
try:
    from game.game import Game
    _probe("[toiletsim] L2 imported Game OK")
except Exception:
    import traceback
    _probe("[toiletsim] L2-FATAL import Game failed:\n" + traceback.format_exc())
    raise


def _set_dpi_aware() -> None:
    # Tell Windows not to scale the window — we manage our own pixels.
    if sys.platform == "win32":
        try:
            import ctypes
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            pass


async def main() -> None:
    _probe("[toiletsim] L3 main() entered")
    _set_dpi_aware()
    _probe("[toiletsim] L4 dpi done, constructing Game()")
    try:
        game = Game()
        _probe("[toiletsim] L5 Game() constructed, starting run loop")
        await game.run()
        _probe("[toiletsim] L6 Game.run() returned")
    except Exception:
        import traceback
        _probe("[toiletsim] FATAL during Game:\n" + traceback.format_exc())
        raise


_probe("[toiletsim] L7 about to call asyncio.run(main())")


# Run unconditionally — pygbag's shell.source() does NOT set __name__ to
# "__main__", so a guard here would skip startup on web. Desktop is unaffected
# because `python src/main.py` already runs main.py as __main__.
asyncio.run(main())
