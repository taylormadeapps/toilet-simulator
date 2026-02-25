# /ts-cap — Commit and Push

Execute immediately — no plan mode.

## Procedure

1. Run `git status` to see all changed and untracked files.
2. Run `git diff --stat` to summarise what changed.
3. Run `git log --oneline -5` for recent commit message style.
4. Draft a concise commit message summarising the changes.
   - Focus on the "why" not the "what".
   - Follow the style of recent commits in the log.
5. Stage relevant files by name. Prefer explicit file paths over `git add -A`.
   - Never stage `.env`, credentials, secrets, or `.DS_Store`.
6. Commit with the message, ending with:
   `Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>`
7. Push to the remote: `git push`.
8. Run `git status` to verify clean state.

## Rules

- A commit is always a push. Never commit without pushing.
- Never commit without explicit developer consent.
- If pre-commit hooks fail, fix the issue, re-stage, and create a NEW commit.
  Never amend unless explicitly asked.
