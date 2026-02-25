# /ts-deploy — Deploy Build to Windows Test Machine

Execute immediately — no plan mode.

## Procedure

1. Run `/ts-test` first — all tests must pass before deploying.
2. Run `/ts-run` to confirm the game launches without errors on Mac.
3. Check the share is mounted:
   ```bash
   ls /Volumes/toiletsim/
   ```
   If not mounted, instruct the developer:
   > Mount the share: Finder → Go → Connect to Server → `smb://192.168.0.21/toiletsim`
   > Auth: Microsoft account login (credentials in Keychain after first connect).

   Wait for confirmation before continuing.

4. Sync the project to the share:
   ```bash
   rsync -av --delete \
     --exclude '.git' \
     --exclude '__pycache__' \
     --exclude '*.pyc' \
     --exclude '.venv' \
     --exclude 'venv' \
     --exclude '.claude' \
     --exclude '.DS_Store' \
     --exclude 'dist' \
     --exclude 'build' \
     --exclude '*.spec' \
     /Users/taylormadeapps/files/toilet\ simulator/ \
     /Volumes/toiletsim/
   ```

5. Verify the deploy:
   ```bash
   ls /Volumes/toiletsim/
   ```
   Confirm `src/`, `assets/`, `requirements.txt`, `run.bat` are all present.

6. Report success with a summary of what was deployed.

## Notes

- The `--delete` flag removes files from the share that no longer exist in
  the source. This keeps the deploy clean — no stale files.
- `.claude` and `.git` are excluded — the deploy is a clean copy of the
  game, not a dev workspace.
- The Windows machine has Python 3.14 and Claude Code installed.
- The tester runs `run.bat` or asks Claude Code to launch the game.
