# TraceLeak NEXT TODO

Current checkpoint: Level 16 completion TODO created; Level 15 local validation pending.

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

Focused validation for the Level 16 planning path:

```powershell
pytest tests/test_level16_pre_handoff_review.py
pytest tests/test_level16_pre_handoff_review_report.py
pytest tests/test_write_level16_files_cli.py
```

## Completed recent blocks

- [x] P147: Level 14 local validation reported all pass.
- [x] P148: added Level 15 validation rollup helper.
- [x] P149: added Level 15 validation rollup Markdown report.
- [x] P150: added Level 15 validation rollup writer CLI.
- [x] P151: updated local validation docs with Level 15 commands.
- [ ] P152: run focused Level 15 tests, `ruff check .`, and full `pytest` locally.
- [x] P153: added Level 16 completion TODO.

## Level roadmap summary

- Level 15: validation rollup.
- Level 16: pre-handoff review planning.

## Current Level 16 TODO

See:

```text
docs/level16-completion-todo.md
```

Recommended next implementation order:

1. P153 pre-handoff review manifest.
2. P154 pre-handoff review report.
3. P155 writer CLI.
4. P156 docs and handoff update.
5. P157 validation checkpoint.

## Candidate next block

Start P153 only after checking Level 15 validation status. Keep Level 16 review-only and path-only.
