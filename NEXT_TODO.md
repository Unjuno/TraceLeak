# TraceLeak NEXT TODO

Current checkpoint: Level 15 validation rollup implemented; local validation pending.

This file is the active short-term TODO. `TODO.md` is kept as historical context and should not be deleted.

## Validation baseline

Run from the repository root:

```powershell
cd C:\Users\junny\Desktop\traceLeak\TraceLeak
git pull --ff-only
ruff check .
pytest
```

Focused validation for the Level 15 validation rollup path:

```powershell
pytest tests/test_level15_validation_rollup.py
pytest tests/test_level15_validation_rollup_report.py
pytest tests/test_write_level15_files_cli.py
```

## Completed recent blocks

- [x] P147: Level 14 local validation reported all pass.
- [x] P148: added Level 15 validation rollup helper.
- [x] P149: added Level 15 validation rollup Markdown report.
- [x] P150: added Level 15 validation rollup writer CLI.
- [x] P151: updated local validation docs with Level 15 commands.
- [ ] P152: run focused Level 15 tests, `ruff check .`, and full `pytest` locally.

## Level roadmap summary

- Level 14: handoff completeness audit.
- Level 15: validation rollup.

## Current Level 15 commands

Generate Level 15 files:

```powershell
traceleak-write-level15-files --out-dir reports/local/level15_validation_rollup
```

Validate Level 15 focused tests:

```powershell
pytest tests/test_level15_validation_rollup.py
pytest tests/test_level15_validation_rollup_report.py
pytest tests/test_write_level15_files_cli.py
```

## Candidate next block after Level 15 all-pass

Do not start Level 16 until P152 is complete. The next block should first create a Level 16 TODO and review checkpoint rather than widening behavior directly.
