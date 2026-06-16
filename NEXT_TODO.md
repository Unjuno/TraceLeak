# TraceLeak NEXT TODO

Current checkpoint: Level 20 implemented; local validation pending.

## Validation baseline

```powershell
cd C:\Users\junny\Desktop\traceLeak\TraceLeak
git pull --ff-only
ruff check .
pytest
```

## Focused validation for Level 20

```powershell
pytest tests/test_level20_closure_index.py
pytest tests/test_level20_closure_index_report.py
pytest tests/test_write_level20_files_cli.py
```

## Completed recent blocks

- [x] P172: Level 19 local validation reported all pass.
- [x] P173: added Level 20 helper.
- [x] P174: added Level 20 report.
- [x] P175: added Level 20 writer CLI.
- [x] P176: updated docs.
- [ ] P177: run local validation.

## Generate Level 20 files

```powershell
traceleak-write-level20-files --out-dir reports/local/level20_closure_index
```
