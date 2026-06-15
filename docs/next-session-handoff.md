# Next session handoff

Current checkpoint: Level 15 validation rollup implemented; local validation pending.

## Local validation

```powershell
cd C:\Users\junny\Desktop\traceLeak\TraceLeak
git pull --ff-only
ruff check .
pytest
```

## Focused checks

```powershell
pytest tests/test_level15_validation_rollup.py
pytest tests/test_level15_validation_rollup_report.py
pytest tests/test_write_level15_files_cli.py
```

## What changed in the latest block

- Added Level 15 validation rollup helper.
- Added Level 15 validation rollup Markdown report renderer.
- Added Level 15 validation rollup writer CLI.
- Registered `traceleak-write-level15-files` entry point.
- Updated local validation docs with Level 15 commands.
- Updated `NEXT_TODO.md` with Level 15 implementation state.

## Level 15 generation command

```powershell
traceleak-write-level15-files --out-dir reports/local/level15_validation_rollup
```

## Current boundary

Level 15 remains review-only and path-only. It records pending local validation state and does not execute validation commands, read artifact contents, perform direct action, or enable claims.

## Next likely work

- Fix any local Level 15 focused test failures first.
- Run `ruff check .`.
- Run full `pytest`.
- If all pass, mark Level 15 complete and create a Level 16 TODO before any further expansion.
