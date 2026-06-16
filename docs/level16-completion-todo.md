# Level 16 Completion TODO

Level 16 is final pre-handoff review planning after Level 15.

Current baseline: Level 15 is implemented but local Level 15 all-pass validation has not been explicitly reported. Level 16 remains review-only and path-only.

## Level 16 goal

Create a final pre-handoff review layer that records whether the Level 15 validation rollup is ready for a later handoff phase.

The Level 16 flow is:

```text
Level 15 validation rollup
  -> pre-handoff review manifest
  -> pre-handoff review report
  -> writer CLI
  -> validation checkpoint
```

## Level 16 non-goals

- No external project build.
- No external project execution.
- No source tree mutation.
- No artifact content parsing.
- No command execution.
- No private material collection.
- No claim generation.

## Level 16 done definition

Level 16 is complete when all of the following are true:

- [x] A versioned pre-handoff review manifest exists.
- [x] The manifest requires a valid Level 15 validation rollup.
- [x] The manifest records validation rollup status.
- [x] The manifest records expected validation commands.
- [x] The manifest records review disposition.
- [x] The manifest remains path-only and review-only.
- [x] A pre-handoff Markdown report exists.
- [x] A writer CLI exists for Level 16 review artifacts.
- [ ] Focused Level 16 tests pass.
- [ ] `ruff check .` passes.
- [ ] Full `pytest` passes.

## P153: pre-handoff review manifest

### Status

- [x] Added Level 16 pre-handoff review helper.
- [x] Defined `traceleak.level16_pre_handoff_review.v1`.
- [x] Required a valid Level 15 validation rollup.
- [x] Recorded source rollup format and phase.
- [x] Recorded source validation status.
- [x] Recorded expected validation commands.
- [x] Recorded review disposition:
  - [x] `ready_after_local_validation` when source validation is pending.
  - [x] `blocked_by_validation_state` for any unsupported state.
- [x] Kept flags:
  - [x] review only true.
  - [x] path only true.
  - [x] content read false.
  - [x] command executed false.
  - [x] claim generated false.
- [x] Added focused tests.

## P154: pre-handoff review report

### Status

- [x] Added Markdown report renderer.
- [x] Rendered review disposition.
- [x] Rendered source validation status.
- [x] Rendered expected validation commands.
- [x] Rendered review-only boundary.
- [x] Rendered local validation commands.
- [x] Rendered next-level preconditions.
- [x] Added focused tests.

## P155: Level 16 writer CLI

### Status

- [x] Added neutral writer CLI name: `traceleak-write-level16-files`.
- [x] Built Level 16 local review artifact.
- [x] Rendered local review report.
- [x] Wrote JSON and Markdown under `reports/local/level16_review/`.
- [x] Did not read artifact contents.
- [x] Did not execute validation commands.
- [x] Did not mutate source trees.
- [x] Did not generate claims.
- [x] Added focused tests.

## P156: docs and handoff update

### Status

- [x] Updated `docs/next-session-handoff.md` with Level 16 status.
- [x] Updated `NEXT_TODO.md` with Level 16 checkpoint.
- [x] Added Level 16 generation command.
- [x] Added Level 16 validation command group.

## P157: Level 16 validation checkpoint

### Commands

```powershell
cd C:\Users\junny\Desktop\traceLeak\TraceLeak
git pull --ff-only
pytest tests/test_level16_pre_handoff_review.py
pytest tests/test_level16_review_report.py
pytest tests/test_write_level16_files_cli.py
ruff check .
pytest
```

### Completion criteria

- [ ] Focused Level 16 tests pass.
- [ ] `ruff check .` passes.
- [ ] Full `pytest` passes.
- [ ] Level 16 output artifacts stay under `reports/local/`.

## Stop condition

Stop before Level 17 unless Level 16 focused tests, `ruff check .`, and full `pytest` all pass locally.
