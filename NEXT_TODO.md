# TraceLeak NEXT TODO

Current checkpoint: Level 18 archive-index layer implemented; local validation pending.

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
- [x] P163: added Level 18 archive-index helper.
- [x] P164: added Level 18 archive-index Markdown report.
- [x] P165: added Level 18 archive-index writer CLI.
- [x] P166: updated local validation docs with Level 18 commands.
- [ ] P167: run focused Level 18 tests, `ruff check .`, and full `pytest` locally.

## Level roadmap summary

- Level 17: release-readiness checklist.
- Level 18: archive index.

## Current Level 18 commands

Generate Level 18 files:

```powershell
traceleak-write-level18-files --out-dir reports/local/level18_archive_index
```

Validate Level 18 focused tests:

```powershell
pytest tests/test_level18_archive_index.py
pytest tests/test_level18_archive_index_report.py
pytest tests/test_write_level18_files_cli.py
```

## Candidate next block after Level 18 all-pass

Do not start Level 19 until P167 is complete. The next block should first create a Level 19 TODO and review checkpoint rather than widening behavior directly.
