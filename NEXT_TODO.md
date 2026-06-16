# TraceLeak NEXT TODO

Current checkpoint: Level 17 completion TODO created; implementation pending.

This file is the active short-term TODO. `TODO.md` is kept as historical context and should not be deleted.

## Validation baseline

Run from the repository root:

```powershell
cd C:\Users\junny\Desktop\traceLeak\TraceLeak
git pull --ff-only
ruff check .
pytest
```

Focused validation for Level 17:

```powershell
pytest tests/test_level17_release_readiness.py
pytest tests/test_level17_release_readiness_report.py
pytest tests/test_write_level17_files_cli.py
```

## Completed recent blocks

- [x] P147: Level 14 local validation reported all pass.
- [x] P148: added Level 15 validation rollup helper.
- [x] P149: added Level 15 validation rollup Markdown report.
- [x] P150: added Level 15 validation rollup writer CLI.
- [x] P151: updated local validation docs with Level 15 commands.
- [x] P152: Level 15 local validation reported all pass.
- [x] P153: added Level 16 completion TODO and review helper.
- [x] P154: added Level 16 review Markdown report.
- [x] P155: added Level 16 local review writer CLI.
- [x] P156: registered Level 16 CLI entry point.
- [x] P157: Level 16 local validation reported all pass.
- [x] P158: added Level 17 completion TODO.

## Level roadmap summary

- Level 16: pre-handoff review.
- Level 17: release-readiness checklist planning.

## Current Level 17 TODO

See:

```text
docs/level17-completion-todo.md
```

Recommended next implementation order:

1. P158 release-readiness checklist.
2. P159 release-readiness report.
3. P160 writer CLI.
4. P161 docs and handoff update.
5. P162 validation checkpoint.

## Candidate next block

Start P158 only. Keep Level 17 review-only and path-only.
