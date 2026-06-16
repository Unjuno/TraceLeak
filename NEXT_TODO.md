# TraceLeak NEXT TODO

Current checkpoint: Level 25 implemented; local validation pending.

## Validation baseline

```powershell
cd C:\Users\junny\Desktop\traceLeak\TraceLeak
git pull --ff-only
ruff check .
pytest
```

## Focused validation for Level 25

```powershell
pytest tests/test_level25_index.py
pytest tests/test_level25_index_report.py
pytest tests/test_write_level25_files_cli.py
```

## Completed recent blocks

- [x] P197: Level 24 local validation reported all pass.
- [x] P198: added Level 25 helper.
- [x] P199: added Level 25 report.
- [x] P200: added Level 25 writer CLI.
- [x] P201: updated handoff and next TODO.
- [ ] P202: run local validation.

## Generate Level 25 files

```powershell
traceleak-write-level25-files --out-dir reports/local/level25_index
```
