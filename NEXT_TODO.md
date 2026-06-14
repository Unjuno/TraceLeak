# TraceLeak NEXT TODO

Current checkpoint: Level 7 planning layer implemented and locally reported all pass.

This file is the active short-term TODO. `TODO.md` is kept as historical context and should not be deleted.

## Validation baseline

Run from the repository root:

```powershell
cd C:\Users\junny\Desktop\traceLeak\TraceLeak
git pull --ff-only
ruff check .
pytest
```

Focused validation for the current Level 7 planning path:

```powershell
pytest tests/test_level7_review_gate.py
pytest tests/test_level7_planning_contract.py
pytest tests/test_level7_artifact_boundary_plan.py
pytest tests/test_level7_readiness_artifacts.py
pytest tests/test_write_level7_artifacts_cli.py
```

## Completed recent blocks

- [x] P93: added one-command local report bundle helper.
- [x] P94: added local report bundle smoke tests and CLI.
- [x] P95: local focused tests, `ruff check .`, and full `pytest` reported all pass.
- [x] P96: added OpenSSL-derived metadata profile schema.
- [x] P97: added profile validator hardening.
- [x] P98: added profile-to-adapter bridge.
- [x] P99: added Level 6 profile demo chain.
- [x] P100: added Level 6 Markdown report.
- [x] P101: added Level 6 artifact writer CLI.
- [x] P102: dashboard direct integration deferred; Level 6 artifact CLI covers local generation.
- [x] P103: updated local validation docs for Level 6.
- [x] P104: Level 6 local validation reported all pass.
- [x] P105: added Level 7 readiness review note.
- [x] P106: added Level 7 review gate.
- [x] P107: added Level 7 planning-only contract.
- [x] P108: added Level 7 artifact boundary plan.
- [x] P109: added Level 7 review checklist.
- [x] P110: added Level 7 readiness report.
- [x] P111: added Level 7 planning artifact writer CLI.
- [x] P112: refreshed local validation and handoff docs.
- [x] P113: Level 7 local validation reported all pass.

## Candidate next block

### Level 8: approved metadata artifact intake

Level 8 should remain metadata/report only. It should accept only approved local artifacts under `reports/local/` that match the Level 7 artifact boundary plan.

Do not introduce external builds, external runs, source mutation, raw capture collection, payload collection, private material collection, or claim generation.

### P114: approved artifact intake manifest

- [ ] Define `traceleak.level8_artifact_intake_manifest.v1`.
- [ ] Require a valid Level 7 artifact boundary plan.
- [ ] Accept only artifact classes listed by the boundary plan.
- [ ] Require all paths to be relative and under `reports/local/`.
- [ ] Reject unknown, raw, sensitive, or claim-bearing artifact classes.

### P115: artifact intake validator

- [ ] Validate manifest shape.
- [ ] Validate unique artifact keys.
- [ ] Validate safe relative paths.
- [ ] Validate accepted artifact classes.
- [ ] Keep payload reading disabled.

### P116: path-only intake index

- [ ] Build an index that records path, class, role, existence, and size.
- [ ] Do not read JSON or Markdown payload contents.
- [ ] Record `payload_reading_allowed = false`.
- [ ] Record `claim_generation_allowed = false`.

### P117: Level 8 report

- [ ] Render accepted artifact counts.
- [ ] Render missing artifact counts.
- [ ] Render rejected class policy.
- [ ] State that no payload was read and no claim was generated.

### P118: Level 8 writer CLI

- [ ] Write manifest, path-only index, and report.
- [ ] Keep output under `reports/local/level8_intake/`.
- [ ] Reject unsafe paths and rejected classes.

### P119: validation checkpoint

- [ ] Run focused Level 8 tests.
- [ ] Run `ruff check .`.
- [ ] Run full `pytest`.

Recommended default: start Level 8 with a path-only artifact intake manifest, not runtime work.
