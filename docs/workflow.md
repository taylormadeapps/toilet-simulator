# Toilet Simulator — Workflow & Team Structure

How work gets done. Team structure for parallel Claude Code execution,
slash command reference, and the build/test pipeline.

---

## Team Structure

Claude operates as a PM coordinating specialist teams. The developer is the
CEO — all product decisions escalate to them.

| Team | Personality | Domain | Key Files |
|------|-------------|--------|-----------|
| **Stream Engineers** | Obsessed with fluid dynamics (for a pee game). If the stream doesn't feel right, nothing else matters. | Stream physics, arc maths, pressure scaling, particle systems | `src/systems/physics.py`, `src/entities/stream.py` |
| **Level Designers** | Creative chaos agents. Every level needs a gimmick and a laugh. | Level configs, modifiers (shake, sway), object placement, difficulty curves | `src/systems/level_manager.py`, `assets/maps/` |
| **Sprite Wranglers** | Pixel nerds. Make the belly look good from above. Art direction police. | Sprites, animation, placeholders, visual consistency | `assets/sprites/`, `src/entities/player.py`, `src/entities/toilet.py` |
| **Test Freaks** | If the stream passes through the bowl wall, they will find it. Hate bugs, love edge cases. | Test suite, coverage, physics edge cases, scoring validation | `tests/` |
| **Doc Geeks** | Docs ship with code. Design evolves, docs evolve with it. | All markdown docs, design decisions, architecture updates | `docs/`, `CLAUDE.md` |
| **Build Bob** | The gatekeeper. If `python src/main.py` crashes, nothing else matters. Clean run, tests green — that's the gate. | Entry point, deps, packaging, cross-platform builds | `src/main.py`, `requirements.txt`, build scripts |

---

## Parallel Execution Protocol

### Fan Out (Safe in Parallel)
- Level Designers drafting configs while Stream Engineers tweak physics
- Sprite Wranglers making assets while Test Freaks write collision tests
- Doc Geeks updating docs while any team works on code
- Multiple teams reading/analysing code simultaneously

### Converge (One Writer at a Time)
- Edits to the same file — one team writes, others wait
- Integration after physics changes — test before merging with other work
- Build Bob's gate — run + test is the final convergence point

### Escalation
PM asks CEO (the developer) for:
- Design decisions (scoring model, new mechanics, art direction)
- New dependencies or libraries
- Scope changes or level additions
- Anything that changes what the game IS, not how it's built

Teams do not make product decisions.

---

## Build & Test Pipeline

### Dev Loop (macOS — Primary)

```
1. Write code
2. /ts-run          → Does it launch? Does it crash?
3. /ts-test         → Do all tests pass?
4. Playtest         → Does it feel right?
5. /ts-cap          → Commit and push
```

### Cross-Platform Testing (Windows — Son's PC)

Builds are pushed to the son's Windows PC via **Windows file sharing** for
playtesting each iteration.

#### Build Process

```
1. All tests passing on Mac         (/ts-test)
2. Game runs cleanly on Mac         (/ts-run)
3. Package build for Windows        (/ts-build — see below)
4. Drop build to shared folder      (Windows file share)
5. Son playtests on Windows
6. Feedback loop back to dev
```

#### Packaging for Windows

**Phase 1 (early dev):** Share the raw Python project. Son runs with Python
installed on his machine:
```
python src/main.py
```
Requires Python 3.12+ and pygame-ce installed on the Windows machine.

**Phase 2 (when friction is too high):** Package with PyInstaller to create
a standalone `.exe`:
```
pyinstaller --onefile --windowed src/main.py
```
Drops a single executable into `dist/` — copy to the shared folder.

**Phase 3 (stretch):** Proper installer or zip distribution with bundled assets.

#### File Share Setup
- **Windows share:** `\\JUPITER\toiletsim` (IP: `192.168.0.21`)
- **macOS mount point:** `/Volumes/toiletsim`
  (mount via Finder: Go → Connect to Server → `smb://192.168.0.21/toiletsim`)
- **Auth:** Microsoft account login — `mysterydiner@hotmail.com` has read/write.
  Guest disabled, everyone removed. Credentials stored in macOS Keychain.
- Build artifacts (or raw project) are copied to this share after each
  successful build

---

## Slash Commands

### /ts-cap — Commit and Push

Full procedure in `.claude/commands/ts-cap.md`.

1. `git status` and `git diff --stat` to review changes
2. `git log --oneline -5` for recent commit style
3. Draft a concise commit message
4. Stage relevant files (named files, not `git add -A`)
5. Commit with co-author line
6. Push to remote
7. `git status` to verify

**Rule:** Never commit without explicit developer consent.

### /ts-run — Run the Game

Full procedure in `.claude/commands/ts-run.md`.

1. Check pygame-ce is installed
2. `python src/main.py`
3. Report any errors

### /ts-test — Run Tests

Full procedure in `.claude/commands/ts-test.md`.

1. `SDL_VIDEODRIVER=dummy python -m pytest tests/ -v`
2. Report results and failures

### /ts-deploy — Deploy to Windows Test Machine

Full procedure in `.claude/commands/ts-deploy.md`.

1. Run `/ts-test` — all tests must pass
2. Run `/ts-run` — confirm game launches on Mac
3. Check share is mounted at `/Volumes/toiletsim/`
4. Rsync project to share (excludes `.git`, `__pycache__`, `.claude`, etc.)
5. Verify deploy contents

**Target:** `smb://192.168.0.21/toiletsim` → `/Volumes/toiletsim/`
**Tester runs:** `run.bat` or asks Claude Code to launch the game.

---

## Development Rhythm

The project follows an iterative loop:

```
┌─────────────────────────────────┐
│  1. Pick next feature/level     │
│  2. Plan (lightweight)          │
│  3. Build (code + assets)       │
│  4. Test (automated + manual)   │
│  5. Playtest (Mac)              │
│  6. Ship to Windows for testing │
│  7. Gather feedback             │
│  8. Iterate or move on          │
└─────────────────────────────────┘
```

Each cycle should produce something playable. No multi-day invisible
architecture sprints. If you can't play it, it's not done.
