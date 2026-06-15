# Level 15 Completion TODO

Level 15 is validation rollup planning after Level 14.

Current baseline: Level 14 is locally reported all pass. Level 15 remains review-only and path-only.

## Level 15 goal

Create a validation rollup layer that records whether the Level 14 completeness outputs are ready for later handoff.

The Level 15 flow is:

```text
Level 14 completeness audit
  -> validation rollup manifest
  -> validation rollup report
  -> writer CLI
  -> validation checkpoint
```

## Level 15 non-goals

- No external project build.
- No external project execution.
- No source tree mutation.
- No artifact content parsing.
- No private material collection.
- No claim generation.

## Level 15 done definition

Level 15 is complete when all of the following are true:

- [x] A versioned validation rollup manifest exists.
- [x] The rollup requires a valid Level 14 completeness audit.
- [x] The rollup records completeness status.
- [x] The rollup records required validation command names.
- [x] The rollup records validation status without executing commands.
- [x] The rollup remains path-only and review-only.
- [x] A rollup Markdown report exists.
- [x] A writer CLI exists for Level 15 rollup artifacts.
- [ ] Focused Level 15 tests pass.
- [ ] `ruff check .` passes.
- [ ] Full `pytest` passes.

## P148: validation rollup manifest

### Status

- [x] Added Level 15 validation rollup helper.
- [x] Defined `traceleak.level15_validation_rollup.v1`.
- [x] Required a valid Level 14 completeness audit.
- [x] Recorded source audit format and phase.
- [x] Recorded completeness status.
- [x] Recorded expected local validation commands:
  - [x] focused Level 15 tests.
  - [x] `ruff check .`.
  - [x] full `pytest`.
- [x] Recorded validation state as pending by default.
- [x] Kept flags:
  - [x] review only true.
  - [x] path only true.
  - [x] content read false.
  - [x] command executed false.
  - [x] claim generated false.
- [x] Added focused tests.

## P149: validation rollup report

### Status

- [x] Added Markdown report renderer.
- [x] Rendered rollup status.
- [x] Rendered source completeness status.
- [x] Rendered expected validation commands.
- [x] Rendered pending validation state.
- [x] Rendered review-only boundary.
- [x] Rendered next-level preconditions.
- [x] Added focused tests.

## P150: Level 15 writer CLI

### Status

- [x] Added neutral writer CLI name: `traceleak-write-level15-files`.
- [x] Built Level 15 validation rollup.
- [x] Rendered rollup report.
- [x] Wrote JSON and Markdown under `reports/local/level15_validation_rollup/`.
- [x] Did not read artifact contents.
- [x] Did not execute validation commands.
- [x] Did not mutate source trees.
- [x] Did not generate claims.
- [x] Added focused tests.

## P151: docs and handoff update

### Status

- [x] Updated `docs/local-validation.md` with Level 15 focused commands.
- [x] Updated `docs/next-session-handoff.md` with Level 15 status.
- [x] Updated `NEXT_TODO.md` with Level 15 checkpoint.
- [x] Added Level 15 generation command.
- [x] Added Level 15 validation command group.

## P152: Level 15 validation checkpoint

### Commands

```powershell
cd C:\Users\junny\Desktop\traceLeak\TraceLeak
git pull --ff-only
pytest tests/test_level15_validation_rollup.py
pytest tests/test_level15_validation_rollup_report.py
pytest tests/test_write_level15_files_cli.py
ruff check .
pytest
```

### Completion criteria

- [ ] Focused Level 15 tests pass.
- [ ] `ruff check .` passes.
- [ ] Full `pytest` passes.
- [ ] Level 15 output artifacts stay under `reports/local/`.

## Stop condition

Stop before Level 16 unless Level 15 focused tests, `ruff check .`, and full `pytest` all pass locally.
