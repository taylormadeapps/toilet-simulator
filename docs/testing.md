# Toilet Simulator — Testing Strategy

How to test a game. Not every pixel — every system.

---

## Philosophy

Games are hard to test because the output is visual and subjective. But the
systems underneath are pure logic — physics, scoring, collision, state
transitions. Those are testable. Focus there.

**Test the maths and the logic. Playtest the feel.**

---

## What to Test

| System | What to Verify |
|--------|---------------|
| Stream physics | Particles follow correct arc given initial velocity and gravity |
| Collision | Bowl detection triggers on overlap, floor detection triggers outside bowl |
| Scoring | Points calculated correctly for hits and misses under both scoring models |
| Bladder | Depletes at correct rate, pressure output scales correctly with volume |
| Level modifiers | Earthquake applies correct offset, drunk sway follows correct curve |
| State machine | Scene transitions work, pause actually pauses, results show on level end |
| Input | Pointer position maps correctly to stream aim direction |
| Level loading | Config files parse correctly, all required fields present |
| Object physics | Force from stream moves objects correctly based on mass and friction |

---

## What NOT to Test

- Rendering output (how it looks is a playtest, not a unit test)
- Exact pixel positions (brittle, breaks on resolution changes)
- Artistic choices (sprite quality, colour palette)
- Audio playback (test that sounds are triggered, not how they sound)
- Frame rate (profile manually, not in CI)

---

## Test Framework

**pytest** with pygame-ce running headless.

### Running Tests

```bash
SDL_VIDEODRIVER=dummy python -m pytest tests/ -v
```

The `SDL_VIDEODRIVER=dummy` environment variable runs pygame-ce without a display,
which is required for CI and headless test runs.

On macOS, if dummy driver causes issues:

```bash
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python -m pytest tests/ -v
```

---

## Test Structure

```
tests/
├── conftest.py              # Shared fixtures (pygame-ce init, mock entities)
├── test_physics.py          # Stream arc, gravity, particle movement
├── test_collision.py        # Bowl hit, floor hit, object hit detection
├── test_scoring.py          # Score calculation, combos, level tallying
├── test_bladder.py          # Depletion rate, pressure output, empty trigger
├── test_level_manager.py    # Config parsing, modifier setup, scene building
├── test_states.py           # State transitions, pause/resume, level end
└── test_input.py            # Pointer position mapping, abstraction layer
```

### Naming Convention

- Test files: `tests/test_<module_name>.py`
- Test functions: `test_<what_it_tests>_<expected_outcome>()`
- Example: `test_stream_particle_follows_gravity_arc()`

---

## Fixtures

Common fixtures in `conftest.py`:

```python
@pytest.fixture
def pygame_init():
    """Initialise pygame-ce for test. Teardown after."""
    pygame.init()
    yield
    pygame.quit()

@pytest.fixture
def sample_toilet():
    """Standard toilet with known bowl rect for collision tests."""
    return Toilet(bowl_rect=pygame.Rect(200, 200, 100, 80))

@pytest.fixture
def full_bladder():
    """Bladder at 100% volume."""
    return Bladder(volume=1.0, depletion_rate=0.01)
```

---

## Testing Priority

In order of importance:

1. **Scoring** — if the score is wrong, the game is broken
2. **Collision** — if bowl/floor detection is wrong, scoring is wrong
3. **Bladder** — if depletion is wrong, levels end at wrong times
4. **Stream physics** — if the arc is wrong, aiming feels broken
5. **State machine** — if transitions break, the game is unplayable
6. **Level loading** — if configs don't parse, new levels don't work
7. **Input** — if pointer mapping is wrong, nothing works

---

## Cross-Platform Testing

- **Primary:** macOS (dev machine) — run full test suite locally
- **Secondary:** Windows (son's test machine) — manual playtesting per build
- Tests should pass on both platforms. Use `pathlib.Path` for all file paths
  in tests to avoid separator issues.
