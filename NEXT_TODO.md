# TraceLeak NEXT TODO

Current checkpoint: Level 15 completion TODO created; Level 14 local validation pending.

This file is the active short-term TODO. `TODO.md` is kept as historical context and should not be deleted.

## Validation baseline

Run from the repository root:

```powershell
cd C:\Users\junny\Desktop\traceLeak\TraceLeak
git pull --ff-only
ruff check .
pytest
```

Focused validation for Level 14:

```powershell
pytest tests/test_level14_completeness_audit.py
pytest tests/test_level14_completeness_report.py
pytest tests/test_write_level14_files_cli.py
```

Focused validation for the Level 15 planning path:

```powershell
pytest tests/test_level15_validation_rollup.py
pytest tests/test_level15_validation_rollup_report.py
pytest tests/test_write_level15_files_cli.py
```

## Completed recent blocks

- [x] P142: Level 13 local validation reported all pass.
- [x] P143: added Level 14 completion TODO and completeness audit helper.
- [x] P144: added Level 14 completeness Markdown report.
- [x] P145: added Level 14 completeness writer CLI.
- [x] P146: updated local validation docs with Level 14 commands.
- [ ] P147: run focused Level 14 tests, `ruff check .`, and full `pytest` locally.
- [x] P148: added Level 15 completion TODO.

## Level roadmap summary

- Level 14: handoff completeness audit.
- Level 15: validation rollup planning.

## Current Level 15 TODO

See:

```text
docs/level15-completion-todo.md
```

Recommended next implementation order:

1. P148 validation rollup manifest.
2. P149 validation rollup report.
3. P150 writer CLI.
4. P151 docs and handoff update.
5. P152 validation checkpoint.

## Candidate next block

Start P148 only after checking Level 14 validation status. Keep Level 15 review-only and path-only.
