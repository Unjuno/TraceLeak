# TraceLeak NEXT TODO

Current checkpoint: Level 24 implemented; local validation pending.

## Validation baseline

```powershell
cd C:\Users\junny\Desktop\traceLeak\TraceLeak
git pull --ff-only
ruff check .
pytest
```

## Focused validation for Level 24

```powershell
pytest tests/test_level24_index.py
pytest tests/test_level24_index_report.py
pytest tests/test_write_level24_files_cli.py
```

## Completed recent blocks

- [x] P192: Level 23 local validation reported all pass.
- [x] P193: added Level 24 helper.
- [x] P194: added Level 24 report.
- [x] P195: added Level 24 writer CLI.
- [x] P196: updated handoff and next TODO.
- [ ] P197: run local validation.

## Generate Level 24 files

```powershell
traceleak-write-level24-files --out-dir reports/local/level24_index
```
