# /lll — Launch Local Web Build (pygbag)

Execute immediately — no plan mode, no permission prompts.

Builds the game with pygbag and serves it at http://localhost:8000 so it
can be played in a browser, mirroring the GitHub Pages deployment.

## Procedure

1. Check pygbag is installed: `python -m pip list 2>/dev/null | grep -i ^pygbag`
2. If not found: `python -m pip install pygbag`
3. Kill any existing pygbag background process so the port is free.
4. Stage audio files inside `src/` (NOT inside `src/assets/`).
   pygbag's `pack.py` automatically prepends `assets/` to every bundled
   file, so `src/sounds/...` becomes `assets/sounds/...` in the tarball,
   which extracts to `/data/data/src/assets/sounds/...` at runtime — exactly
   where the template's loaderhome (`/data/data/src/assets/`) expects them.
   ```
   rm -rf src/assets src/sounds
   cp -r assets/sounds src/sounds
   ```
5. Launch pygbag in the background (`run_in_background: true`):
   `python -u -m pygbag --width 312 --height 675 --ume_block 0 --app_name "Toilet Simulator" src/main.py`
6. Poll the output file with an `until` loop until it contains
   `"Serving HTTP"`, then report the URL **http://localhost:8000**.
7. Open the URL in the user's default browser:
   `python -c "import webbrowser; webbrowser.open('http://localhost:8000')"`
8. If the build fails (look for `Traceback` or `Error` in output),
   report the full traceback and skip step 7.

## Notes

- The `-u` flag is REQUIRED — pygbag's stdout is line-buffered without it
  and the background process appears to hang.
- `--ume_block 0` skips the click-to-start media-engagement gate so the
  game starts rendering immediately (audio still requires a click).
- Width/height MUST match `SCREEN_WIDTH`/`SCREEN_HEIGHT` from settings.py.
- DO NOT copy source files into `src/assets/` — pygbag handles the
  `assets/` prefix automatically. Doing it manually produces
  `assets/assets/...` paths which break the runtime.
- Always use `python -m pip` (not bare `pip`).
- `src/sounds/` is regenerated each run from `assets/sounds/`. Both
  `src/sounds/` and `src/assets/` (legacy) are gitignored.
