# Next session handoff

Current checkpoint: Level 20 implemented; local validation pending.

## Local validation

```powershell
cd C:\Users\junny\Desktop\traceLeak\TraceLeak
git pull --ff-only
ruff check .
pytest
```

## Focused checks

```powershell
pytest tests/test_level20_closure_index.py
pytest tests/test_level20_closure_index_report.py
pytest tests/test_write_level20_files_cli.py
```

## Latest changes

- Added Level 20 helper.
- Added Level 20 report.
- Added Level 20 writer CLI.
- Registered Level 20 writer entry point.
- Updated local validation docs.

## Next work

Run focused Level 20 tests, `ruff check .`, and full `pytest` locally.
