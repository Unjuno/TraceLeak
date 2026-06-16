# Next session handoff

Current checkpoint: Level 23 implemented; local validation pending.

## Local validation

```powershell
cd C:\Users\junny\Desktop\traceLeak\TraceLeak
git pull --ff-only
ruff check .
pytest
```

## Focused checks

```powershell
pytest tests/test_level23_index.py
pytest tests/test_level23_index_report.py
pytest tests/test_write_level23_files_cli.py
```

## Latest changes

- Added Level 23 helper.
- Added Level 23 report.
- Added Level 23 writer CLI.
- Registered Level 23 writer entry point.
- Updated local validation docs.

## Next work

Run focused Level 23 tests, `ruff check .`, and full `pytest` locally.
