# TraceLeak NEXT TODO

Current checkpoint: Level 20 completion TODO created; implementation pending.

This file is the active short-term TODO. `TODO.md` is kept as historical context and should not be deleted.

## Validation baseline

Run from the repository root:

```powershell
cd C:\Users\junny\Desktop\traceLeak\TraceLeak
git pull --ff-only
ruff check .
pytest
```

Focused validation for Level 20:

```powershell
pytest tests/test_level20_closure_index.py
pytest tests/test_level20_closure_index_report.py
pytest tests/test_write_level20_files_cli.py
```

## Completed recent blocks

- [x] P152: Level 15 local validation reported all pass.
- [x] P157: Level 16 local validation reported all pass.
- [x] P162: Level 17 local validation reported all pass.
- [x] P167: Level 18 local validation reported all pass.
- [x] P172: Level 19 local validation reported all pass.
- [x] P173: added Level 20 completion TODO.

## Level roadmap summary

- Level 19: summary layer.
- Level 20: closure-index planning.

## Current Level 20 TODO

See:

```text
docs/level20-completion-todo.md
```

Recommended next implementation order:

1. P173 closure index.
2. P174 closure-index report.
3. P175 writer CLI.
4. P176 docs and handoff update.
5. P177 validation checkpoint.

## Candidate next block

Start P173 only. Keep Level 20 review-only and path-only.
