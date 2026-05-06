"""Toilet Simulator — Entry Point."""

import asyncio
import ctypes
import sys

from game.game import Game


def _set_dpi_aware() -> None:
    # Tell Windows not to scale the window — we manage our own pixels.
    if sys.platform == "win32":
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            pass


async def main() -> None:
    _set_dpi_aware()
    game = Game()
    await game.run()


if __name__ == "__main__":
    asyncio.run(main())
