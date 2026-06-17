# TraceLeak NEXT TODO

Current checkpoint: Level 26 implemented; local validation pending.

## Validation baseline

```powershell
cd C:\Users\junny\Desktop\traceLeak\TraceLeak
git pull --ff-only
ruff check .
pytest
```

## Focused validation for Level 26

```powershell
pytest tests/test_level26_index.py
pytest tests/test_level26_index_report.py
pytest tests/test_write_level26_files_cli.py
```

## Completed recent blocks

- [x] P202: Level 25 local validation reported all pass.
- [x] P203: added Level 26 helper.
- [x] P204: added Level 26 report.
- [x] P205: added Level 26 writer CLI.
- [x] P206: updated handoff and next TODO.
- [ ] P207: run local validation.

## Generate Level 26 files

```powershell
traceleak-write-level26-files --out-dir reports/local/level26_index
```
