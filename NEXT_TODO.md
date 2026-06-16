# TraceLeak NEXT TODO

Current checkpoint: Level 16 review layer implemented; local validation pending.

This file is the active short-term TODO. `TODO.md` is kept as historical context and should not be deleted.

## Validation baseline

Run from the repository root:

```powershell
cd C:\Users\junny\Desktop\traceLeak\TraceLeak
git pull --ff-only
ruff check .
pytest
```

Focused validation for Level 15:

```powershell
pytest tests/test_level15_validation_rollup.py
pytest tests/test_level15_validation_rollup_report.py
pytest tests/test_write_level15_files_cli.py
```

Focused validation for the Level 16 review path:

```powershell
pytest tests/test_level16_pre_handoff_review.py
pytest tests/test_level16_review_report.py
pytest tests/test_write_level16_files_cli.py
```

## Completed recent blocks

- [x] P147: Level 14 local validation reported all pass.
- [x] P148: added Level 15 validation rollup helper.
- [x] P149: added Level 15 validation rollup Markdown report.
- [x] P150: added Level 15 validation rollup writer CLI.
- [x] P151: updated local validation docs with Level 15 commands.
- [ ] P152: run focused Level 15 tests, `ruff check .`, and full `pytest` locally.
- [x] P153: added Level 16 completion TODO and review helper.
- [x] P154: added Level 16 review Markdown report.
- [x] P155: added Level 16 local review writer CLI.
- [x] P156: registered Level 16 CLI entry point.
- [ ] P157: run focused Level 16 tests, `ruff check .`, and full `pytest` locally.

## Level roadmap summary

- Level 15: validation rollup.
- Level 16: pre-handoff review.

## Current Level 16 commands

Generate Level 16 files:

```powershell
traceleak-write-level16-files --out-dir reports/local/level16_review
```

Validate Level 16 focused tests:

```powershell
pytest tests/test_level16_pre_handoff_review.py
pytest tests/test_level16_review_report.py
pytest tests/test_write_level16_files_cli.py
```

## Candidate next block after Level 16 all-pass

Do not start Level 17 until P157 is complete. The next block should first create a Level 17 TODO and review checkpoint rather than widening behavior directly.
