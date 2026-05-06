"""Game class — fixed-timestep loop and state machine."""

from __future__ import annotations

import asyncio
import sys

import pygame

from game.settings import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, WINDOW_TITLE
from game.states import SplashState, PlayingState, ResultsState, LevelSelectState
from game.levels import compute_stars, PASS_STARS
from systems.input_handler import update_cursor, reset_cursor
from systems.level_manager import LevelManager

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
        self.level_manager = LevelManager()
        self.state: SplashState | PlayingState | ResultsState | LevelSelectState = SplashState(self.level_manager)
        self.running = True

    # ------------------------------------------------------------------
    # Main loop
    # ------------------------------------------------------------------

    async def run(self) -> None:
        """Fixed-timestep accumulator loop."""
        accumulator = 0.0

        while self.running:
            # Raw frame time in seconds, clamped
            frame_time = min(self.clock.tick(FPS) / 1000.0, MAX_FRAME_TIME)
            accumulator += frame_time

            # Update virtual cursor from relative mouse delta
            update_cursor()

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

            # Yield to the browser event loop (required by pygbag)
            await asyncio.sleep(0)

        pygame.quit()

    # ------------------------------------------------------------------
    # State machine
    # ------------------------------------------------------------------

    def _playing_config(self) -> dict:
        """Level config enriched with the 1-based level number."""
        return {**self.level_manager.current_config(),
                "level_number": self.level_manager.current_level + 1}

    def _check_transitions(self) -> None:
        """Read the current state's transition flag and switch if set."""
        transition = getattr(self.state, "transition", None)
        if transition is None:
            return

        if transition == "play":
            self.state = PlayingState(self._playing_config())
            _grab_mouse(True)
            reset_cursor()

        elif transition == "results":
            data = getattr(self.state, "results_data", {})
            acc_s, score_s, overall = compute_stars(data["accuracy"], data["score"])
            self.level_manager.record_result(overall)
            lm = self.level_manager
            data.update({
                "level_number": lm.current_level + 1,
                "level_name": lm.current_config()["name"],
                "acc_stars": acc_s,
                "score_stars": score_s,
                "overall_stars": overall,
                "can_advance": overall >= PASS_STARS and lm.current_level + 1 < lm.level_count,
            })
            self.state = ResultsState(data)
            _grab_mouse(False)

        elif transition == "next_level":
            self.level_manager.advance()
            self.state = PlayingState(self._playing_config())
            _grab_mouse(True)
            reset_cursor()

        elif transition == "retry":
            self.state = PlayingState(self._playing_config())
            _grab_mouse(True)
            reset_cursor()

        elif transition == "level_select":
            self.state = LevelSelectState(self.level_manager)
            _grab_mouse(False)

        elif transition == "play_level":
            self.state = PlayingState(self._playing_config())
            _grab_mouse(True)
            reset_cursor()

        elif transition == "splash":
            self.state = SplashState(self.level_manager)
            _grab_mouse(False)

        elif transition == "quit":
            _grab_mouse(False)
            self.running = False


def _grab_mouse(grab: bool) -> None:
    """Hide cursor and confine mouse to window, or release."""
    pygame.mouse.set_visible(not grab)
    try:
        pygame.event.set_grab(grab)
    except Exception:
        pass  # not supported in browser
