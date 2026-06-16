# TraceLeak NEXT TODO

Current checkpoint: Level 19 completion TODO created; implementation pending.

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
- [x] P168: added Level 19 completion TODO.

## Level roadmap summary

- Level 18: archive index.
- Level 19: handoff-summary planning.

## Current Level 19 TODO

See:

```text
docs/level19-completion-todo.md
```

Recommended next implementation order:

1. P168 handoff summary.
2. P169 handoff-summary report.
3. P170 writer CLI.
4. P171 docs and handoff update.
5. P172 validation checkpoint.

## Candidate next block

Start P168 only. Keep Level 19 review-only and path-only.
