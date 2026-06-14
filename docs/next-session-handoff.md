# Next session handoff

Current checkpoint: Level 8 approved local artifact intake implemented; local validation pending.

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
```

## What changed in the latest block

- Added Level 1 to Level 8 roadmap summary in `NEXT_TODO.md`.
- Added Level 8 artifact intake helper.
- Added Level 8 approved manifest validation.
- Added Level 8 path-only index.
- Added Level 8 intake Markdown report.
- Added Level 8 local file writer CLI.
- Registered `traceleak-write-level8-files` entry point.
- Updated local validation docs with Level 8 commands.

## Level 8 generation command

```powershell
traceleak-write-level8-files --out-dir reports/local/level8_intake --root-dir .
```

## Current boundary

Level 8 remains path-only local metadata/report artifact intake. The implementation records artifact path, class, role, existence, and size only. It does not parse artifact contents or generate claims.

## Next likely work

- Fix any local Level 8 focused test failures first.
- Run `ruff check .`.
- Run full `pytest`.
- If all pass, mark Level 8 complete and create a Level 9 TODO before any further expansion.
