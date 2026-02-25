# Toilet Simulator — Architecture

Technical blueprint for the codebase. How the code is structured, what goes
where, and the pygame-ce-specific rules that keep things performant and sane.

---

## Source Tree

```
src/
├── main.py              # Entry point. Inits pygame-ce, creates Game, runs loop.
├── game/
│   ├── __init__.py
│   ├── game.py          # Top-level Game class. Owns the loop and state machine.
│   ├── states.py        # State machine: Menu, Playing, Paused, Results
│   └── settings.py      # Constants: screen size, FPS target, colours, paths
├── entities/
│   ├── __init__.py
│   ├── player.py        # Player (belly, position, owns the stream origin)
│   ├── toilet.py        # Toilet (bowl rect/mask, rim, position)
│   ├── stream.py        # Pee stream (particles, arc, collision points)
│   └── objects.py       # Movable objects (mass, friction, position)
├── systems/
│   ├── __init__.py
│   ├── physics.py       # Stream arc calculation, object force, gravity
│   ├── collision.py     # Stream vs bowl, stream vs floor, stream vs objects
│   ├── scoring.py       # Score tracking, combo streaks, level tallying
│   ├── bladder.py       # Bladder volume, depletion rate, pressure output
│   ├── input_handler.py # Pointer abstraction (mouse/touch → screen position)
│   └── level_manager.py # Level loading, config parsing, modifier application
└── ui/
    ├── __init__.py
    ├── hud.py           # Bladder meter, score display, combo indicator
    ├── menu.py          # Main menu, level select
    └── results.py       # End-of-level results screen
```

---

## Game Loop

Fixed timestep with variable rendering. Physics updates at a constant rate
regardless of frame rate.

```
TICK_RATE = 60  # physics updates per second
dt = 1 / TICK_RATE

while running:
    handle_events()        # poll input, queue actions
    accumulator += clock.tick() / 1000

    while accumulator >= dt:
        update(dt)         # fixed-step physics, scoring, bladder
        accumulator -= dt

    render()               # draw current state, interpolate if needed
```

The key rule: `update()` always receives the same `dt`. Frame rate drops
affect rendering smoothness, not physics accuracy.

---

## State Machine

Every screen is a state. The Game class owns a state stack or current state
reference.

| State | Description |
|-------|-------------|
| `SplashState` | Title screen. Click or SPACE to play, ESC to quit. |
| `PlayingState` | Active gameplay. Mouse-Y pressure, physics, scoring. ESC → splash. |
| `ResultsState` | Level complete. Score breakdown. Click or SPACE → splash, ESC → quit. |

Transitions are explicit via `self.transition` string. The Game class reads
the flag and switches state. States do not reference each other directly.
Mouse is grabbed (hidden + confined) during PlayingState, released otherwise.

---

## Entity Model

No ECS. No deep inheritance. Simple classes with composition.

- **Player:** Position, belly sprite, stream origin point. Stationary entity.
- **Toilet:** Position, bowl rect (target zone), rim rect, floor zone.
  Bowl and rim are collision areas, not visual-only.
- **Stream:** List of particles or a curve. Each particle has position,
  velocity, alive/dead state. Particles spawn at stream origin, follow an
  arc, and die on collision.
- **MovableObject:** Position, sprite, mass, friction. Receives force from
  stream particles on collision.

Entities own their data. Systems operate on entities. Entities do not call
systems — systems pull data from entities, compute, and push results back.

---

## Stream Physics

The stream is modelled as a series of particles emitted from the stream origin.

- **Emission:** Particles spawn per-tick at the origin with initial velocity
  aimed upward toward the pointer position. Rate: 3 particles per tick.
- **Gravity:** Particles accelerate downward (150 px/s²). This decelerates
  upward-moving particles, creating a natural arc that peaks and falls.
- **Spread:** Small random angle offset (±0.08 rad) for realism.
- **Speed:** Interpolated between STREAM_MIN_SPEED (100) and
  STREAM_BASE_SPEED (500) based on mouse-Y pressure (0.0–1.0).
- **Pressure:** Driven by mouse Y position, NOT bladder volume. Higher
  mouse = more pressure = faster particles = higher arc = reaches bowl.
- **Collision:** Particles fly freely while ascending (vy ≤ 0). Scored only
  when descending (vy > 0). Bowl hits register inside the ellipse, floor
  hits register when particles fall below the bowl.
- **Particle cap:** 200 max. Oldest alive particle recycled when at cap.

This is 2D — gravity creates a visual arc, not literal 3D physics.

---

## Collision Detection

pygame-ce rect and mask-based. No external physics engine.

| Collision | Method | Result |
|-----------|--------|--------|
| Stream → Bowl | Ellipse equation (descending only) | Score point, kill particle, splash FX |
| Stream → Centre | Inner ellipse (40% of bowl radii) | Bonus point, kill particle, splash FX |
| Stream → Floor | Particle below bowl bottom (descending) | Penalty, kill particle, splash FX |
| Stream → Off-screen | Bounds check (±20px margin) | Kill silently, no score |

Collision is checked per stream particle per tick. Only descending particles
(vy > 0) are evaluated — ascending particles fly freely through the bowl zone.
Bowl and centre zones use ellipse equations, not rectangle collision.

---

## Level Loading

Levels are defined as config data (Python dicts or JSON files in `assets/maps/`).

A level config specifies:
- Bowl size and position
- Bladder starting volume and depletion rate
- Active modifiers (shake, sway, etc.)
- Movable objects (type, position, mass, friction)
- Scoring model (penalty or reward, thresholds)

The level manager reads the config, builds the scene, and hands it to the
Playing state. No level logic lives in the state machine itself.

---

## Input Abstraction

All pointing input resolves to a single value: **pointer position in screen
space** (x, y pixels).

```python
# input_handler.py
def get_pointer_position() -> tuple[int, int]:
    """Return current pointer position. Mouse now, touch later."""
    return pygame.mouse.get_pos()
```

Game mechanics consume this position. They never call `pygame.mouse` directly.
When mobile port happens, only `input_handler.py` changes — everything else
stays the same.

---

## pygame-ce-Specific Rules

These prevent common pygame-ce performance traps:

1. **Surfaces at init, not per-frame.** Create all surfaces during scene
   setup. Never call `pygame.Surface()` inside the game loop.
2. **`convert_alpha()` on all loaded images.** Every `pygame.image.load()`
   call must be followed by `.convert_alpha()` for transparency performance.
3. **Cache fonts at init.** Never create `pygame.font.Font` objects in the
   game loop. Load once, reuse.
4. **Minimise blit calls.** Batch where possible. Use `pygame.sprite.Group`
   for managed drawing when it helps.
5. **Event pump every frame.** Always call `pygame.event.get()` every frame,
   even if you don't use all events. Failing to pump events freezes the OS
   window.
6. **`pygame.display.flip()` or `update()`.** Use `flip()` for full redraws.
   Use `update(rects)` for dirty-rect optimisation if needed later.

---

## Performance Rules

1. **Target:** 60 FPS minimum on the dev machine.
2. **Profile before optimising.** Use `cProfile` or pygame-ce's clock to
   identify actual bottlenecks. No premature Cython, Numpy, or C extensions.
3. **Pure Python first.** Optimise only proven hot paths.
4. **Particle count budget:** Set a reasonable max particle count per stream.
   If it looks good with 30 particles, don't spawn 300.

---

## Cross-Platform Notes

- **Dev machine:** macOS (Tahoe). Primary build and test environment.
- **Test machine:** Windows laptop (JUPITER) via SMB share at `//JUPITER/toiletsim`.
  Deploy via rsync. Auth: `mysterydiner@hotmail.com`.
- **Screen:** 390×844 pixels (iPhone 14/15 portrait logical resolution, 9:19.5).
- **pygame-ce is cross-platform** but test on both platforms per iteration.
- **Path handling:** Always use `pathlib.Path` or `os.path.join()`. Never
  hardcode `/` or `\` separators.
- **Line endings:** Git handles this via `.gitattributes` if needed.
- **Asset paths:** Relative to project root. Use `settings.py` to define
  base paths.
