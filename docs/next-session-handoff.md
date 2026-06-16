# Next session handoff

Current checkpoint: Level 24 implemented; local validation pending.

## Local validation

```powershell
cd C:\Users\junny\Desktop\traceLeak\TraceLeak
git pull --ff-only
ruff check .
pytest
```

## Focused checks

```powershell
pytest tests/test_level24_index.py
pytest tests/test_level24_index_report.py
pytest tests/test_write_level24_files_cli.py
```

## Latest changes

- Added Level 24 helper.
- Added Level 24 report.
- Added Level 24 writer CLI.
- Registered Level 24 writer entry point.
- Updated `NEXT_TODO.md`.

## Next work

Run focused Level 24 tests, `ruff check .`, and full `pytest` locally.
