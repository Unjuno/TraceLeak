# Next session handoff

Current checkpoint: Level 25 implemented; local validation pending.

## Local validation

```powershell
cd C:\Users\junny\Desktop\traceLeak\TraceLeak
git pull --ff-only
ruff check .
pytest
```

## Focused checks

```powershell
pytest tests/test_level25_index.py
pytest tests/test_level25_index_report.py
pytest tests/test_write_level25_files_cli.py
```

## Latest changes

- Level 24 local validation was reported all pass.
- Added Level 25 helper.
- Added Level 25 report.
- Added Level 25 writer CLI.
- Registered Level 25 writer entry point.
- Updated `NEXT_TODO.md`.

## Next work

Run focused Level 25 tests, `ruff check .`, and full `pytest` locally.
