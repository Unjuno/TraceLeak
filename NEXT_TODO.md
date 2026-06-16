# TraceLeak NEXT TODO

Current checkpoint: Level 18 completion TODO created; implementation pending.

This file is the active short-term TODO. `TODO.md` is kept as historical context and should not be deleted.

## Validation baseline

Run from the repository root:

```powershell
cd C:\Users\junny\Desktop\traceLeak\TraceLeak
git pull --ff-only
ruff check .
pytest
```

Focused validation for Level 18:

```powershell
pytest tests/test_level18_archive_index.py
pytest tests/test_level18_archive_index_report.py
pytest tests/test_write_level18_files_cli.py
```

## Completed recent blocks

- [x] P152: Level 15 local validation reported all pass.
- [x] P157: Level 16 local validation reported all pass.
- [x] P162: Level 17 local validation reported all pass.
- [x] P163: added Level 18 completion TODO.

## Level roadmap summary

- Level 17: release-readiness checklist.
- Level 18: archive-index planning.

## Current Level 18 TODO

See:

```text
docs/level18-completion-todo.md
```

Recommended next implementation order:

1. P163 archive index.
2. P164 archive-index report.
3. P165 writer CLI.
4. P166 docs and handoff update.
5. P167 validation checkpoint.

## Candidate next block

Start P163 only. Keep Level 18 review-only and path-only.
