"""Game class — fixed-timestep loop and state machine."""

from __future__ import annotations

import sys

import pygame

from game.settings import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, WINDOW_TITLE
from game.states import SplashState, PlayingState, ResultsState

# Fixed timestep: 60 ticks per second, decoupled from render rate.
TICK_RATE = 60
DT = 1.0 / TICK_RATE
MAX_FRAME_TIME = 0.25  # clamp to avoid spiral-of-death on slow machines


class Game:
    """Top-level game object. Owns the loop and state machine."""

    def __init__(self) -> None:
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(WINDOW_TITLE)
        self.clock = pygame.time.Clock()
        self.state: SplashState | PlayingState | ResultsState = SplashState()
        self.running = True

    # ------------------------------------------------------------------
    # Main loop
    # ------------------------------------------------------------------

    def run(self) -> None:
        """Fixed-timestep accumulator loop."""
        accumulator = 0.0

        while self.running:
            # Raw frame time in seconds, clamped
            frame_time = min(self.clock.tick(FPS) / 1000.0, MAX_FRAME_TIME)
            accumulator += frame_time

            # Gather events once per frame
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False

            # Let state handle events
            self.state.handle_events(events)

            # Fixed-step updates
            while accumulator >= DT:
                self.state.update(DT)
                accumulator -= DT

            # Render
            self.state.draw(self.screen)
            pygame.display.flip()

            # State transitions
            self._check_transitions()

        pygame.quit()
        sys.exit()

    # ------------------------------------------------------------------
    # State machine
    # ------------------------------------------------------------------

    def _check_transitions(self) -> None:
        """Read the current state's transition flag and switch if set."""
        transition = getattr(self.state, "transition", None)
        if transition is None:
            return

        if transition == "play":
            self.state = PlayingState()
            _grab_mouse(True)

        elif transition == "results":
            data = getattr(self.state, "results_data", {})
            self.state = ResultsState(data)
            _grab_mouse(False)

        elif transition == "splash":
            self.state = SplashState()
            _grab_mouse(False)

        elif transition == "quit":
            _grab_mouse(False)
            self.running = False


def _grab_mouse(grab: bool) -> None:
    """Hide cursor and confine mouse to window, or release."""
    pygame.mouse.set_visible(not grab)
    pygame.event.set_grab(grab)
