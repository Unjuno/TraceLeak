# Level 14 Completion TODO

Level 14 is handoff completeness audit planning after Level 13.

Current baseline: Level 13 is locally reported all pass. Level 14 remains review-only and path-only. It audits Level 13 handoff inventory metadata without parsing artifact contents or widening behavior.

## Level 14 goal

Create a handoff completeness audit for the Level 13 handoff inventory.

The Level 14 flow is:

```text
Level 13 handoff inventory
  -> completeness audit
  -> missing-family summary
  -> completeness report
  -> writer CLI
  -> validation checkpoint
```

## Level 14 non-goals

- No external project build.
- No external project execution.
- No source tree mutation.
- No patch materialization.
- No raw capture collection.
- No payload collection.
- No private material collection.
- No artifact content parsing.
- No claim generation.

## Level 14 done definition

Level 14 is complete when all of the following are true:

- [x] A versioned completeness audit exists.
- [x] The audit requires a valid Level 13 handoff inventory.
- [x] The audit records family count and path count.
- [x] The audit records missing family names when required families are absent.
- [x] The audit remains path-only.
- [x] A completeness Markdown report exists.
- [x] A writer CLI exists for Level 14 completeness artifacts.
- [ ] Focused Level 14 tests pass.
- [ ] `ruff check .` passes.
- [ ] Full `pytest` passes.

## P143: completeness audit

### Status

- [x] Added Level 14 completeness audit helper.
- [x] Defined `traceleak.level14_completeness_audit.v1`.
- [x] Required a valid Level 13 handoff inventory.
- [x] Recorded source inventory format and phase.
- [x] Recorded family count.
- [x] Recorded total path count.
- [x] Recorded required families:
  - [x] `level6_profile`
  - [x] `level7_planning`
  - [x] `level8_intake`
  - [x] `level9_readiness`
  - [x] `level10_review`
  - [x] `level11_next_todo`
  - [x] `level12_checkpoint`
- [x] Recorded missing required families.
- [x] Recorded completeness status:
  - [x] `complete` when no required family is missing.
  - [x] `incomplete` otherwise.
- [x] Kept flags:
  - [x] path only true.
  - [x] content read false.
  - [x] claim generated false.
- [x] Added focused tests.

## P144: completeness report

### Status

- [x] Added Markdown report renderer.
- [x] Rendered completeness status.
- [x] Rendered required families.
- [x] Rendered missing families.
- [x] Rendered handoff family counts.
- [x] Rendered path-only boundary.
- [x] Rendered local validation commands.
- [x] Added focused tests.

## P145: Level 14 writer CLI

### Status

- [x] Added neutral writer CLI name: `traceleak-write-level14-files`.
- [x] Built Level 13 closure artifacts.
- [x] Built Level 14 completeness audit.
- [x] Rendered completeness report.
- [x] Wrote JSON and Markdown under `reports/local/level14_completeness/`.
- [x] Did not read artifact contents.
- [x] Did not execute external commands.
- [x] Did not mutate source trees.
- [x] Did not generate claims.
- [x] Added focused tests.

## P146: docs and handoff update

### Status

- [x] Updated `docs/local-validation.md` with Level 14 focused commands.
- [x] Updated `docs/next-session-handoff.md` with Level 14 status.
- [x] Updated `NEXT_TODO.md` with Level 14 checkpoint.
- [x] Added Level 14 generation command.
- [x] Added Level 14 validation command group.

## P147: Level 14 validation checkpoint

### Commands

```powershell
cd C:\Users\junny\Desktop\traceLeak\TraceLeak
git pull --ff-only
pytest tests/test_level14_completeness_audit.py
pytest tests/test_level14_completeness_report.py
pytest tests/test_write_level14_files_cli.py
ruff check .
pytest
```

### Completion criteria

- [ ] Focused Level 14 tests pass.
- [ ] `ruff check .` passes.
- [ ] Full `pytest` passes.
- [ ] Level 14 output artifacts stay under `reports/local/`.

## Stop condition

Stop before Level 15 unless Level 14 focused tests, `ruff check .`, and full `pytest` all pass locally.
