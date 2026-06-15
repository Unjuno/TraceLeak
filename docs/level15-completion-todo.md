# Level 15 Completion TODO

Level 15 is validation rollup planning after Level 14.

Current baseline: Level 14 implementation exists, but local Level 14 all-pass validation has not been explicitly reported in this turn. Level 15 must remain review-only and path-only.

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

- [ ] A versioned validation rollup manifest exists.
- [ ] The rollup requires a valid Level 14 completeness audit.
- [ ] The rollup records completeness status.
- [ ] The rollup records required validation command names.
- [ ] The rollup records validation status without executing commands.
- [ ] The rollup remains path-only and review-only.
- [ ] A rollup Markdown report exists.
- [ ] A writer CLI exists for Level 15 rollup artifacts.
- [ ] Focused Level 15 tests pass.
- [ ] `ruff check .` passes.
- [ ] Full `pytest` passes.

## P148: validation rollup manifest

### Purpose

Define a validation rollup manifest over the Level 14 completeness audit.

### Implementation tasks

- [ ] Add Level 15 validation rollup helper.
- [ ] Define `traceleak.level15_validation_rollup.v1`.
- [ ] Require a valid Level 14 completeness audit.
- [ ] Record source audit format and phase.
- [ ] Record completeness status.
- [ ] Record expected local validation commands:
  - [ ] focused Level 15 tests.
  - [ ] `ruff check .`.
  - [ ] full `pytest`.
- [ ] Record validation state as pending by default.
- [ ] Keep flags:
  - [ ] review only true.
  - [ ] path only true.
  - [ ] content read false.
  - [ ] command executed false.
  - [ ] claim generated false.

### Tests

- [ ] Build rollup from complete audit.
- [ ] Build rollup from incomplete audit.
- [ ] Reject invalid source audit format.
- [ ] Reject content read enabled.
- [ ] Reject command executed enabled.
- [ ] Reject claim generated enabled.
- [ ] Validate JSON writer.

## P149: validation rollup report

### Purpose

Render a Markdown report for Level 15 validation rollup.

### Required sections

- [ ] Rollup status.
- [ ] Source completeness status.
- [ ] Expected validation commands.
- [ ] Pending validation state.
- [ ] Review-only boundary.
- [ ] Next-level preconditions.

### Tests

- [ ] Report contains required headings.
- [ ] Report states review-only boundary.
- [ ] Report states no commands were executed.
- [ ] Report states no content was read.
- [ ] Report states no claim was generated.

## P150: Level 15 writer CLI

### Purpose

Expose Level 15 rollup artifact generation.

### Implementation tasks

- [ ] Add neutral writer CLI name.
- [ ] Build Level 14 completeness artifacts.
- [ ] Build Level 15 validation rollup.
- [ ] Render rollup report.
- [ ] Write JSON and Markdown under `reports/local/level15_validation_rollup/`.
- [ ] Do not read artifact contents.
- [ ] Do not execute validation commands.
- [ ] Do not mutate source trees.
- [ ] Do not generate claims.

### Tests

- [ ] CLI writes validation rollup manifest.
- [ ] CLI writes validation rollup report.
- [ ] CLI rejects bad reviewer or unsafe output path.

## P151: docs and handoff update

### Documentation tasks

- [ ] Update `docs/local-validation.md` with Level 15 focused commands.
- [ ] Update `docs/next-session-handoff.md` with Level 15 status.
- [ ] Update `NEXT_TODO.md` with Level 15 checkpoint.
- [ ] Add Level 15 generation command.
- [ ] Add Level 15 validation command group.

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

## Recommended implementation order

1. P148 validation rollup manifest.
2. P149 validation rollup report.
3. P150 writer CLI.
4. P151 docs and handoff update.
5. P152 validation checkpoint.

## Stop condition

Stop before Level 16 unless Level 15 focused tests, `ruff check .`, and full `pytest` all pass locally.
