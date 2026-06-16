# TraceLeak NEXT TODO

Current checkpoint: Level 21 implemented; local validation pending.

## Validation baseline

```powershell
cd C:\Users\junny\Desktop\traceLeak\TraceLeak
git pull --ff-only
ruff check .
pytest
```

## Focused validation for Level 21

```powershell
pytest tests/test_level21_status_index.py
pytest tests/test_level21_status_index_report.py
pytest tests/test_write_level21_files_cli.py
```

## Completed recent blocks

- [x] P177: Level 20 local validation reported all pass.
- [x] P178: added Level 21 helper.
- [x] P179: added Level 21 report.
- [x] P180: added Level 21 writer CLI.
- [x] P181: updated docs.
- [ ] P182: run local validation.

## Generate Level 21 files

```powershell
traceleak-write-level21-files --out-dir reports/local/level21_status_index
```
