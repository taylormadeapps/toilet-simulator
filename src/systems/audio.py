"""Pee audio — seamless random sample cycling with flow-driven volume."""

import random

import pygame

from game.settings import ASSETS_DIR

_SND_DIR = ASSETS_DIR / "pee sounds"
_FLOOR_DIR = _SND_DIR / "floor"
_PEE_CHANNEL = 2          # dedicated mixer channel so we can control it precisely
_FLOOR_CHANNEL = 3        # dedicated channel for floor-hit audio
_QUEUE_AHEAD = 0.3        # seconds before end of current sample to queue the next
_FADEOUT_MS = 250         # ms to fade out when flow stops
_VOL_RISE = 20.0          # volume units/sec when ramping up (fast snap-in)
_VOL_FALL = 3.0           # volume units/sec when ramping down (slow decay, prevents flicker)
_BOWL_HIT_VOL = 0.2       # volume contribution per bowl-only hit (max 0.4)
_BOWL_VOL_CAP = 0.4       # bowl-only hits can never reach max volume
# Centre hits always drive volume to 1.0 — max is reserved for dead-centre aim
_FLOOR_HIT_VOL = 1.0      # volume contribution per floor hit
_FLOOR_VOL_CAP = 1.0      # floor audio can reach full volume


class PeeAudio:
    """Cycles through pee samples randomly and seamlessly.

    Call update() every frame with the current flow rate (0.0–1.0).
    Volume tracks flow directly — louder when pushing harder.
    Samples are queued ahead of time so there is no audible gap on the join.
    The same sample never plays twice in a row.
    """

    def __init__(self) -> None:
        self._samples = [
            pygame.mixer.Sound(str(_SND_DIR / "real wee.wav")),
            pygame.mixer.Sound(str(_SND_DIR / "fake pee1.wav")),
            pygame.mixer.Sound(str(_SND_DIR / "fake pee2.wav")),
            pygame.mixer.Sound(str(_SND_DIR / "fake pee3.wav")),
        ]
        self._ch = pygame.mixer.Channel(_PEE_CHANNEL)
        self._last_idx: int = -1
        self._elapsed: float = 0.0
        self._current_len: float = 0.0
        self._queued: bool = False
        self._flowing: bool = False
        self._volume: float = 0.0   # smoothed current volume, 0.0–1.0

    def _pick(self) -> pygame.mixer.Sound:
        """Return a random sample, never repeating the previous one."""
        choices = [i for i in range(len(self._samples)) if i != self._last_idx]
        self._last_idx = random.choice(choices)
        return self._samples[self._last_idx]

    def update(
        self, dt: float, flow: float, bowl_hits: int = 0, centre_hits: int = 0,
    ) -> None:
        """Call every frame.

        flow        — stream pressure 0.0–1.0 (gates audio; no flow = silence)
        bowl_hits   — particles that landed in bowl (not centre) this frame
        centre_hits — particles that landed in centre zone this frame
        Volume ramps toward target smoothly: centre hits = 1.0 max,
        bowl-only hits scale up to 0.8, no hits decays to 0.
        """
        # Derive target volume from hit counts this frame
        if flow < 0.01:
            target = 0.0
        elif centre_hits > 0:
            target = 1.0
        elif bowl_hits > 0:
            target = min(bowl_hits * _BOWL_HIT_VOL, _BOWL_VOL_CAP)
        else:
            target = 0.0

        # Smooth toward target — fast rise, slow fall (avoids flicker between landings)
        if target > self._volume:
            self._volume = min(self._volume + _VOL_RISE * dt, target)
        else:
            self._volume = max(self._volume - _VOL_FALL * dt, target)

        active = self._volume > 0.01

        if not active:
            if self._flowing:
                self._ch.fadeout(_FADEOUT_MS)
                self._flowing = False
                self._elapsed = 0.0
                self._queued = False
            return

        # Apply smoothed volume every frame
        self._ch.set_volume(self._volume)

        if not self._flowing:
            # Kick off the first sample
            snd = self._pick()
            self._current_len = snd.get_length()
            self._elapsed = 0.0
            self._queued = False
            self._ch.play(snd)
            self._flowing = True
            return

        self._elapsed += dt

        # Queue the next sample before the current one ends to avoid gaps
        if not self._queued and self._elapsed >= self._current_len - _QUEUE_AHEAD:
            self._ch.queue(self._pick())
            self._queued = True

        # Rolled over into the next sample — update length tracking
        if self._elapsed >= self._current_len:
            overflow = self._elapsed - self._current_len
            self._current_len = self._samples[self._last_idx].get_length()
            self._elapsed = overflow
            self._queued = False

    def stop(self) -> None:
        """Hard stop — call on state exit."""
        self._ch.stop()
        self._flowing = False


class FloorAudio:
    """Cycles floor-hit samples randomly and seamlessly.

    Same algorithm as PeeAudio but driven by floor_hits per frame.
    More floor hits = louder. Blends naturally with PeeAudio on its own channel.
    """

    def __init__(self) -> None:
        self._samples = [
            pygame.mixer.Sound(str(_FLOOR_DIR / "floor1.wav")),
            pygame.mixer.Sound(str(_FLOOR_DIR / "floor2.wav")),
            pygame.mixer.Sound(str(_FLOOR_DIR / "floor3.wav")),
            pygame.mixer.Sound(str(_FLOOR_DIR / "floor4.wav")),
            pygame.mixer.Sound(str(_FLOOR_DIR / "floor5.wav")),
        ]
        self._ch = pygame.mixer.Channel(_FLOOR_CHANNEL)
        self._last_idx: int = -1
        self._elapsed: float = 0.0
        self._current_len: float = 0.0
        self._queued: bool = False
        self._flowing: bool = False
        self._volume: float = 0.0

    def _pick(self) -> pygame.mixer.Sound:
        choices = [i for i in range(len(self._samples)) if i != self._last_idx]
        self._last_idx = random.choice(choices)
        return self._samples[self._last_idx]

    def update(self, dt: float, flow: float, floor_hits: int = 0) -> None:
        """Call every frame.

        flow       — stream pressure 0.0–1.0 (gates audio; no flow = silence)
        floor_hits — particles that landed on the floor this frame
        """
        if flow < 0.01:
            target = 0.0
        else:
            target = min(floor_hits * _FLOOR_HIT_VOL, _FLOOR_VOL_CAP)

        if target > self._volume:
            self._volume = min(self._volume + _VOL_RISE * dt, target)
        else:
            self._volume = max(self._volume - _VOL_FALL * dt, target)

        active = self._volume > 0.01

        if not active:
            if self._flowing:
                self._ch.fadeout(_FADEOUT_MS)
                self._flowing = False
                self._elapsed = 0.0
                self._queued = False
            return

        self._ch.set_volume(self._volume)

        if not self._flowing:
            snd = self._pick()
            self._current_len = snd.get_length()
            self._elapsed = 0.0
            self._queued = False
            self._ch.play(snd)
            self._flowing = True
            return

        self._elapsed += dt

        if not self._queued and self._elapsed >= self._current_len - _QUEUE_AHEAD:
            self._ch.queue(self._pick())
            self._queued = True

        if self._elapsed >= self._current_len:
            overflow = self._elapsed - self._current_len
            self._current_len = self._samples[self._last_idx].get_length()
            self._elapsed = overflow
            self._queued = False

    def stop(self) -> None:
        """Hard stop — call on state exit."""
        self._ch.stop()
        self._flowing = False
