# Next session handoff

Current checkpoint: Level 18 completion TODO created; implementation pending.

## Local validation

```powershell
cd C:\Users\junny\Desktop\traceLeak\TraceLeak
git pull --ff-only
ruff check .
pytest
```

## Focused checks

```powershell
pytest tests/test_level18_archive_index.py
pytest tests/test_level18_archive_index_report.py
pytest tests/test_write_level18_files_cli.py
```

## What changed in the latest block

- Level 17 was locally reported all pass.
- Marked Level 17 validation complete.
- Added `docs/level18-completion-todo.md`.
- Updated `NEXT_TODO.md` with Level 18 planning state.

## Level 17 generation command

```powershell
traceleak-write-level17-files --out-dir reports/local/level17_release_readiness
```

## Level 18 TODO

```text
docs/level18-completion-todo.md
```

## Current boundary

Level 18 is planned as a review-only, path-only archive index. It must not read artifact contents, execute validation commands, perform direct action, or enable claims.

## Next likely work

- Start P163 archive index.
- Then implement P164 archive-index report.
- Then implement P165 writer CLI.
- Run focused Level 18 tests, `ruff check .`, and full `pytest` before Level 19.
