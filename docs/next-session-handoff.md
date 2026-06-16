# Next session handoff

Current checkpoint: Level 22 implemented; local validation pending.

## Local validation

```powershell
cd C:\Users\junny\Desktop\traceLeak\TraceLeak
git pull --ff-only
ruff check .
pytest
```

## Focused checks

```powershell
pytest tests/test_level22_index.py
pytest tests/test_level22_index_report.py
pytest tests/test_write_level22_files_cli.py
```

## Latest changes

- Added Level 22 helper.
- Added Level 22 report.
- Added Level 22 writer CLI.
- Registered Level 22 writer entry point.
- Updated local validation docs.

## Next work

Run focused Level 22 tests, `ruff check .`, and full `pytest` locally.
