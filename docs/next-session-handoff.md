# Next session handoff

Current checkpoint: Level 17 completion TODO created; implementation pending.

## Local validation

```powershell
cd C:\Users\junny\Desktop\traceLeak\TraceLeak
git pull --ff-only
ruff check .
pytest
```

## Focused checks

```powershell
pytest tests/test_level17_release_readiness.py
pytest tests/test_level17_release_readiness_report.py
pytest tests/test_write_level17_files_cli.py
```

## What changed in the latest block

- Level 16 was locally reported all pass.
- Marked Level 16 validation complete.
- Added `docs/level17-completion-todo.md`.
- Updated `NEXT_TODO.md` with Level 17 planning state.

## Level 16 generation command

```powershell
traceleak-write-level16-files --out-dir reports/local/level16_review
```

## Level 17 TODO

```text
docs/level17-completion-todo.md
```

## Current boundary

Level 17 is planned as a review-only, path-only release-readiness checklist. It must not read artifact contents, execute validation commands, perform direct action, or enable claims.

## Next likely work

- Start P158 release-readiness checklist.
- Then implement P159 release-readiness report.
- Then implement P160 writer CLI.
- Run focused Level 17 tests, `ruff check .`, and full `pytest` before Level 18.
