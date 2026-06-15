# TraceLeak NEXT TODO

Current checkpoint: Level 14 completeness layer implemented; local validation pending.

This file is the active short-term TODO. `TODO.md` is kept as historical context and should not be deleted.

## Validation baseline

Run from the repository root:

```powershell
cd C:\Users\junny\Desktop\traceLeak\TraceLeak
git pull --ff-only
ruff check .
pytest
```

Focused validation for the current Level 14 completeness path:

```powershell
pytest tests/test_level14_completeness_audit.py
pytest tests/test_level14_completeness_report.py
pytest tests/test_write_level14_files_cli.py
```

## Completed recent blocks

- [x] P142: Level 13 local validation reported all pass.
- [x] P143: added Level 14 completion TODO and completeness audit helper.
- [x] P144: added Level 14 completeness Markdown report.
- [x] P145: added Level 14 completeness writer CLI.
- [x] P146: updated local validation docs with Level 14 commands.
- [ ] P147: run focused Level 14 tests, `ruff check .`, and full `pytest` locally.

## Level roadmap summary

- Level 13: checkpoint closure and handoff inventory.
- Level 14: handoff completeness audit.

## Current Level 14 commands

Generate Level 14 files:

```powershell
traceleak-write-level14-files --out-dir reports/local/level14_completeness --root-dir .
```

Validate Level 14 focused tests:

```powershell
pytest tests/test_level14_completeness_audit.py
pytest tests/test_level14_completeness_report.py
pytest tests/test_write_level14_files_cli.py
```

## Candidate next block after Level 14 all-pass

Do not start Level 15 until P147 is complete. The next block should first create a Level 15 TODO and review checkpoint rather than widening behavior directly.
