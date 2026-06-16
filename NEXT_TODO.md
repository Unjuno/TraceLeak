# TraceLeak NEXT TODO

Current checkpoint: Level 19 summary layer implemented; local validation pending.

This file is the active short-term TODO. `TODO.md` is kept as historical context and should not be deleted.

## Validation baseline

Run from the repository root:

```powershell
cd C:\Users\junny\Desktop\traceLeak\TraceLeak
git pull --ff-only
ruff check .
pytest
```

Focused validation for Level 19:

```powershell
pytest tests/test_level19_handoff_summary.py
pytest tests/test_level19_handoff_summary_report.py
pytest tests/test_write_level19_files_cli.py
```

## Completed recent blocks

- [x] P152: Level 15 local validation reported all pass.
- [x] P157: Level 16 local validation reported all pass.
- [x] P162: Level 17 local validation reported all pass.
- [x] P167: Level 18 local validation reported all pass.
- [x] P168: added Level 19 summary helper.
- [x] P169: added Level 19 summary Markdown report.
- [x] P170: added Level 19 summary writer CLI.
- [x] P171: updated local validation docs with Level 19 commands.
- [ ] P172: run focused Level 19 tests, `ruff check .`, and full `pytest` locally.

## Level roadmap summary

- Level 18: archive index.
- Level 19: summary layer.

## Current Level 19 commands

Generate Level 19 files:

```powershell
traceleak-write-level19-files --out-dir reports/local/level19_handoff_summary
```

Validate Level 19 focused tests:

```powershell
pytest tests/test_level19_handoff_summary.py
pytest tests/test_level19_handoff_summary_report.py
pytest tests/test_write_level19_files_cli.py
```

## Candidate next block after Level 19 all-pass

Do not start Level 20 until P172 is complete. The next block should first create a Level 20 TODO and review checkpoint rather than widening behavior directly.
