# Next session handoff

Current checkpoint: Level 21 implemented; local validation pending.

## Local validation

```powershell
cd C:\Users\junny\Desktop\traceLeak\TraceLeak
git pull --ff-only
ruff check .
pytest
```

## Focused checks

```powershell
pytest tests/test_level21_status_index.py
pytest tests/test_level21_status_index_report.py
pytest tests/test_write_level21_files_cli.py
```

## Latest changes

- Added Level 21 helper.
- Added Level 21 report.
- Added Level 21 writer CLI.
- Registered Level 21 writer entry point.
- Updated local validation docs.

## Next work

Run focused Level 21 tests, `ruff check .`, and full `pytest` locally.
