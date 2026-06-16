# Next session handoff

Current checkpoint: Level 17 release-readiness layer implemented; local validation pending.

## Local validation

```powershell
cd C:\Users\junny\Desktop\traceLeak\TraceLeak
git pull --ff-only
ruff check .
pytest
```

## Focused checks

```powershell
pytest tests/test_level17_release_readiness.py
pytest tests/test_level17_release_readiness_report.py
pytest tests/test_write_level17_files_cli.py
```

## What changed in the latest block

- Added Level 17 release-readiness helper.
- Added Level 17 release-readiness Markdown report renderer.
- Added Level 17 release-readiness writer CLI.
- Registered `traceleak-write-level17-files` entry point.
- Updated local validation docs with Level 17 commands.
- Updated `NEXT_TODO.md` with Level 17 implementation state.

## Level 17 generation command

```powershell
traceleak-write-level17-files --out-dir reports/local/level17_release_readiness
```

## Current boundary

Level 17 remains review-only and path-only. It records pending local validation state and does not read artifact contents, execute validation commands, perform direct action, or enable claims.

## Next likely work

- Fix any local Level 17 focused test failures first.
- Run `ruff check .`.
- Run full `pytest`.
- If all pass, mark Level 17 complete and create a Level 18 TODO before any further expansion.
