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
| `Menu` | Main menu. Start game, level select, quit. |
| `Playing` | Active gameplay. Runs physics, input, rendering. |
| `Paused` | Gameplay frozen. Overlay with resume/quit options. |
| `Results` | Level complete. Shows score breakdown, star rating, next level. |

Transitions are explicit. No state can transition to another state without
going through the Game class. States do not reference each other directly.

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

- **Emission:** Particles spawn per-frame at the origin with initial velocity
  aimed toward the pointer position.
- **Gravity:** Particles accelerate downward (toward the floor plane in 2D).
- **Spread:** Small random offset applied to initial velocity for realism.
- **Pressure:** Bladder volume scales initial particle speed. Full bladder =
  fast particles = longer reach and more force. Near-empty = slow, droopy.
- **Lifetime:** Particles die on collision with bowl, floor, or objects.
  Dead particles trigger scoring and visual effects (splash).

This is 2D — "gravity" is simulated as a visual arc on the stream shape,
not literal 3D physics. Keep it simple enough to feel right, not physically
accurate.

---

## Collision Detection

pygame-ce rect and mask-based. No external physics engine.

| Collision | Method | Result |
|-----------|--------|--------|
| Stream → Bowl | Rect or mask overlap | Score point, kill particle, splash FX |
| Stream → Floor | Particle outside bowl rect | Penalty, kill particle, puddle FX |
| Stream → Object | Rect overlap | Apply force to object, kill particle |
| Stream → Rim | Edge detection (stretch) | Splash in random direction |

Collision is checked per stream particle per frame. If this becomes a
bottleneck, spatial partitioning can be added — but profile first.

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
- **Test machine:** Windows PC (son's machine via file sharing).
- **pygame-ce is cross-platform** but test on both platforms per iteration.
- **Path handling:** Always use `pathlib.Path` or `os.path.join()`. Never
  hardcode `/` or `\` separators.
- **Line endings:** Git handles this via `.gitattributes` if needed.
- **Asset paths:** Relative to project root. Use `settings.py` to define
  base paths.
