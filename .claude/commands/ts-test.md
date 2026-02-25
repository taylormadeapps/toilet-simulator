# /ts-test — Run Test Suite

Execute immediately — no plan mode, no permission prompts.

## Procedure

1. Run the test suite:
   ```bash
   SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python -m pytest tests/ -v
   ```
2. Report results.
3. If any tests fail, summarise which tests failed and why.
4. If the `tests/` directory does not exist or is empty, report that no tests
   exist yet.

## Notes

- `SDL_VIDEODRIVER=dummy` runs Pygame without a display (headless).
- `SDL_AUDIODRIVER=dummy` prevents audio device errors on headless runs.
- Both are required for CI and headless environments.
