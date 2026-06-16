# TraceLeak NEXT TODO

Current checkpoint: Level 23 implemented; local validation pending.

## Validation baseline

```powershell
cd C:\Users\junny\Desktop\traceLeak\TraceLeak
git pull --ff-only
ruff check .
pytest
```

## Focused validation for Level 23

```powershell
pytest tests/test_level23_index.py
pytest tests/test_level23_index_report.py
pytest tests/test_write_level23_files_cli.py
```

## Completed recent blocks

- [x] P187: Level 22 local validation reported all pass.
- [x] P188: added Level 23 helper.
- [x] P189: added Level 23 report.
- [x] P190: added Level 23 writer CLI.
- [x] P191: updated docs.
- [ ] P192: run local validation.

## Generate Level 23 files

```powershell
traceleak-write-level23-files --out-dir reports/local/level23_index
```
