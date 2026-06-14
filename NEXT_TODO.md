# TraceLeak NEXT TODO

Current checkpoint: Level 9 readiness audit implemented; local validation pending.

This file is the active short-term TODO. `TODO.md` is kept as historical context and should not be deleted.

## Validation baseline

Run from the repository root:

```powershell
cd C:\Users\junny\Desktop\traceLeak\TraceLeak
git pull --ff-only
ruff check .
pytest
```

Focused validation for the current Level 9 readiness path:

```powershell
pytest tests/test_level9_readiness_audit.py
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
- [x] P114: added Level 8 artifact intake manifest.
- [x] P115: added Level 8 manifest validator hardening.
- [x] P116: added Level 8 path-only intake index.
- [x] P117: added Level 8 intake Markdown report.
- [x] P118: added Level 8 file writer CLI.
- [x] P119: updated local validation docs with Level 8 commands.
- [x] P120: Level 8 local validation reported all pass.
- [x] P121: added Level 9 readiness audit helper.
- [x] P122: added Level 9 readiness Markdown report.
- [x] P123: added Level 9 readiness writer CLI.
- [ ] P124: run focused Level 9 tests, `ruff check .`, and full `pytest` locally.

## Level 1 to Level 9 roadmap summary

- Level 1: core validation, feature extraction, baseline/report surface.
- Level 2: model-sequence samples and lightweight model checks.
- Level 3: MLP report chain and review summaries.
- Level 4: contract and approval scaffolding.
- Level 5: metadata demo bundle and local report surfaces.
- Level 6: metadata profile ingress and adapter/model/report proof.
- Level 7: review-gated planning, boundary plan, checklist, readiness report.
- Level 8: approved local metadata/report artifact intake, path-only index, intake report.
- Level 9: readiness audit over the Level 8 path-only index.

## Current Level 9 commands

Generate Level 9 files:

```powershell
traceleak-write-level9-files --out-dir reports/local/level9_readiness --root-dir .
```

Validate Level 9 focused tests:

```powershell
pytest tests/test_level9_readiness_audit.py
```

## Candidate next block after Level 9 all-pass

Do not start Level 10 until P124 is complete. The next block should first create a Level 10 TODO and review checkpoint rather than widening behavior directly.
