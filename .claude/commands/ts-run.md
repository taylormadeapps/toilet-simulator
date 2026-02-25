# /ts-run — Run the Game

Execute immediately — no plan mode, no permission prompts.

## Procedure

1. Check Pygame is installed: `pip list 2>/dev/null | grep -i pygame`
2. If Pygame is not found: `pip install -r requirements.txt`
3. Run the game: `python src/main.py`
4. Report any errors or crashes with full traceback.

## Notes

- If the game is already running in a background process, kill it first.
- If `src/main.py` does not exist yet, report that the entry point is missing.
