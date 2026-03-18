# /ts-run — Run the Game

Execute immediately — no plan mode, no permission prompts.

## Procedure

1. Check pygame-ce is installed: `python -m pip list 2>/dev/null | grep -i pygame-ce`
2. If pygame-ce is not found: `python -m pip install -r requirements.txt`
3. Launch the game in the background: `python src/main.py` (use `run_in_background: true`)
4. Wait 3 seconds, then check the output file for any errors or crashes and report them with full traceback.

## Notes

- Always use `python -m pip` (not bare `pip`) to ensure the correct Python environment is used.
- Launch the game as a background process so the window opens without blocking the terminal.
- If the game is already running in a background process, kill it first.
- If `src/main.py` does not exist yet, report that the entry point is missing.
