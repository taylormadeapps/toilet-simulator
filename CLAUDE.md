# Toilet Simulator — Rules of Engagement

These rules govern how any Claude Code instance operates on this codebase.
They are non-negotiable unless explicitly renegotiated with the developer in conversation.

Claude is a builder's assistant, not an architect. Toilet Simulator is a fun,
irreverent Pygame game, not an engine showcase. The goal is to ship a playable
game with tight mechanics and escalating humour — not to build a general-purpose
game framework. If a change increases complexity without making the game funnier
or more fun to play, reject it.

---

## 1. Core Philosophy — Ship the Game

Toilet Simulator exists to make people laugh while they aim. Gameplay over
architecture. Playable builds over perfect abstractions.

Every decision filters through one question: does this make the game more fun
to play right now? If the answer is "maybe, eventually, architecturally" — it
waits. If the answer is "yes, now, for players" — it ships.

**Default bias:** fewer systems, fewer abstractions, more playable levels.

---

## 2. Project Overview

**Stack:** Python 3.12+, Pygame 2.x
**Perspective:** 2D top-down, looking down past a big belly at a toilet
**Core mechanic:** Aim pee stream into toilet bowl, don't hit the floor
**Target platform:** Desktop (mouse) now, mobile (touch) later

### Key Paths

| Path | Purpose |
|------|---------|
| `src/` | All game source code |
| `src/main.py` | Entry point |
| `src/game/` | Game loop, state machine, scene management |
| `src/entities/` | Player, toilet, stream, objects |
| `src/systems/` | Physics, scoring, input, level management |
| `src/ui/` | Menus, HUD, overlays |
| `assets/` | Sprites, audio, fonts, level data |
| `tests/` | Test suite |
| `docs/` | Extended governance and design docs |

---

## 3. Game Loop Laws (Non-Negotiable)

The game loop must remain:
- Fixed timestep for physics (decouple update from render)
- No blocking I/O in the game loop
- State machine driven — every screen is a state (menu, playing, paused, results)
- Input handling is polled per frame, never callback-spaghetti

---

## 4. Iterative Development Law

Development is level-by-level, mechanic-by-mechanic:
1. Get one level fully playable before building the next
2. New mechanics are prototyped in isolation, then integrated
3. No speculative systems — build what the current level needs
4. Playtest before polish

See [docs/game-design.md](docs/game-design.md) for full game design,
level progression, and mechanic catalogue.

---

## 5. Input Abstraction

Mouse aiming now. Touchscreen aiming later. The input system must resolve
all pointing input to a **screen-space pointer position** — nothing else.

Game mechanics consume a pointer position. They do not know or care whether
it came from a mouse, a finger, or a gamepad stick. Keep the mechanic
pointer-agnostic so mobile is a natural port, not a rewrite.

---

## 6. No Feature Creep Without Approval

Claude must not introduce:
- New libraries or dependencies
- New game systems or mechanics
- Asset generation beyond what is requested
- Major refactors or rewrites

without explicit developer request.

No rewrites. No premature optimisation. No "just in case" architecture.
Small stable increments only.

**Never commit or push without explicit developer consent.** Wait for
`/ts-cap` or a clear instruction to commit. Do not proactively commit
after completing work.

A commit to git is always a push. Never commit without pushing.

When adding, modifying, or removing functionality, always update the relevant
documentation under `docs/`. Docs ship with code.

---

## 7. Code Philosophy — Essential Complexity Only

Fight tooth and nail to keep things to essential complexity. Every line must
earn its place. This is a fun game, not enterprise software.

- **Clarity over cleverness.** Write code any Python developer could read.
- **No hero functions.** Split past ~60 lines.
- **No class hierarchy hell.** Favour composition. A flat data structure
  you can see beats an inheritance tree you have to imagine.
- **Comment the why, not the what.**
- **Type hints everywhere.** Use Python type hints for all function signatures.

See [docs/architecture.md](docs/architecture.md) for code structure conventions
and Pygame-specific patterns.

---

## 8. The Prime Directive

Toilet Simulator is not here to be a game engine.

It is here to:
- Make people laugh
- Ship playable levels
- Iterate fast
- Stay simple

**Ship the game.**

---

## Extended Documentation

Detailed governance lives in `docs/` to keep this file lean:

| Document | Covers |
|----------|--------|
| [docs/game-design.md](docs/game-design.md) | Game concept, mechanics, levels, scoring, power-ups |
| [docs/architecture.md](docs/architecture.md) | Code structure, Pygame patterns, module conventions |
| [docs/art-and-assets.md](docs/art-and-assets.md) | Asset pipeline, naming, formats, sprite standards |
| [docs/testing.md](docs/testing.md) | Testing strategy, what to test, how to test a game |
| [docs/workflow.md](docs/workflow.md) | Team structure, parallel execution, slash commands |

---

## Slash Commands

| Command | Purpose |
|---------|---------|
| `/ts-cap` | Commit and push |
| `/ts-run` | Run the game |
| `/ts-test` | Run test suite |

See `.claude/commands/` for full command procedures.
