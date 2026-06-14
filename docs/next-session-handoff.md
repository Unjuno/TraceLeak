# Next session handoff

Current checkpoint: Level 9 readiness audit implemented; local validation pending.

## Local validation

```powershell
cd C:\Users\junny\Desktop\traceLeak\TraceLeak
git pull --ff-only
ruff check .
pytest
```

## Focused checks

```powershell
pytest tests/test_openssl_derived_metadata_profile.py
pytest tests/test_openssl_derived_metadata_profile_demo_chain.py
pytest tests/test_openssl_derived_metadata_profile_report.py
pytest tests/test_write_level6_artifacts_cli.py
pytest tests/test_level7_review_gate.py
pytest tests/test_level7_planning_contract.py
pytest tests/test_level7_artifact_boundary_plan.py
pytest tests/test_level7_readiness_artifacts.py
pytest tests/test_write_level7_artifacts_cli.py
pytest tests/test_level8_artifact_intake_manifest.py
pytest tests/test_level8_artifact_intake_index.py
pytest tests/test_level8_artifact_intake_report.py
pytest tests/test_write_level8_files_cli.py
pytest tests/test_level9_readiness_audit.py
```

## What changed in the latest block

- Level 8 was locally reported all pass.
- Added Level 9 readiness audit helper.
- Added Level 9 readiness Markdown report renderer.
- Added Level 9 readiness writer CLI.
- Registered `traceleak-write-level9-files` entry point.
- Updated local validation docs with Level 9 commands.
- Updated `NEXT_TODO.md` with Level 1 to Level 9 roadmap summary.

## Level 9 generation command

```powershell
traceleak-write-level9-files --out-dir reports/local/level9_readiness --root-dir .
```

## Current boundary

Level 9 audits the Level 8 path-only index. It summarizes present and missing local artifact paths and does not parse artifact contents.

## Known limitation

The Level 9 CLI smoke test file could not be added because the GitHub write was blocked by safety checks. The CLI itself is registered and can be smoke-tested manually with the command above.

## Next likely work

- Fix any local Level 9 focused test failures first.
- Run `ruff check .`.
- Run full `pytest`.
- If all pass, mark Level 9 complete and create a Level 10 TODO before any further expansion.
