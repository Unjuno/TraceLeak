# TraceLeak NEXT TODO

Current checkpoint: Level 22 implemented; local validation pending.

## Validation baseline

```powershell
cd C:\Users\junny\Desktop\traceLeak\TraceLeak
git pull --ff-only
ruff check .
pytest
```

## Focused validation for Level 22

```powershell
pytest tests/test_level22_index.py
pytest tests/test_level22_index_report.py
pytest tests/test_write_level22_files_cli.py
```

## Completed recent blocks

- [x] P182: Level 21 local validation reported all pass.
- [x] P183: added Level 22 helper.
- [x] P184: added Level 22 report.
- [x] P185: added Level 22 writer CLI.
- [x] P186: updated docs.
- [ ] P187: run local validation.

## Generate Level 22 files

```powershell
traceleak-write-level22-files --out-dir reports/local/level22_index
```
