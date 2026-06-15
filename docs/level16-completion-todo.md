# Level 16 Completion TODO

Level 16 is final pre-handoff review planning after Level 15.

Current baseline: Level 15 is implemented but local Level 15 all-pass validation has not been explicitly reported. Level 16 must remain review-only and path-only.

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

- [ ] A versioned pre-handoff review manifest exists.
- [ ] The manifest requires a valid Level 15 validation rollup.
- [ ] The manifest records validation rollup status.
- [ ] The manifest records expected validation commands.
- [ ] The manifest records review disposition.
- [ ] The manifest remains path-only and review-only.
- [ ] A pre-handoff Markdown report exists.
- [ ] A writer CLI exists for Level 16 pre-handoff artifacts.
- [ ] Focused Level 16 tests pass.
- [ ] `ruff check .` passes.
- [ ] Full `pytest` passes.

## P153: pre-handoff review manifest

### Purpose

Define a pre-handoff review manifest over the Level 15 validation rollup.

### Implementation tasks

- [ ] Add Level 16 pre-handoff review helper.
- [ ] Define `traceleak.level16_pre_handoff_review.v1`.
- [ ] Require a valid Level 15 validation rollup.
- [ ] Record source rollup format and phase.
- [ ] Record source validation status.
- [ ] Record expected validation commands.
- [ ] Record review disposition:
  - [ ] `ready_after_local_validation` when source validation is pending.
  - [ ] `blocked_by_validation_state` for any unsupported state.
- [ ] Keep flags:
  - [ ] review only true.
  - [ ] path only true.
  - [ ] content read false.
  - [ ] command executed false.
  - [ ] claim generated false.

### Tests

- [ ] Build manifest from pending Level 15 rollup.
- [ ] Reject invalid source rollup format.
- [ ] Reject content read enabled.
- [ ] Reject command executed enabled.
- [ ] Reject claim generated enabled.
- [ ] Validate JSON writer.

## P154: pre-handoff review report

### Purpose

Render a Markdown report for Level 16 pre-handoff review.

### Required sections

- [ ] Review disposition.
- [ ] Source validation status.
- [ ] Expected validation commands.
- [ ] Review-only boundary.
- [ ] Local validation commands.
- [ ] Next-level preconditions.

### Tests

- [ ] Report contains required headings.
- [ ] Report states review-only boundary.
- [ ] Report states no commands were executed.
- [ ] Report states no content was read.
- [ ] Report states no claim was generated.

## P155: Level 16 writer CLI

### Purpose

Expose Level 16 pre-handoff review artifact generation.

### Implementation tasks

- [ ] Add neutral writer CLI name.
- [ ] Build Level 15 validation rollup fixture.
- [ ] Build Level 16 pre-handoff review.
- [ ] Render pre-handoff report.
- [ ] Write JSON and Markdown under `reports/local/level16_pre_handoff/`.
- [ ] Do not read artifact contents.
- [ ] Do not execute validation commands.
- [ ] Do not mutate source trees.
- [ ] Do not generate claims.

### Tests

- [ ] CLI writes pre-handoff review manifest.
- [ ] CLI writes pre-handoff review report.
- [ ] CLI rejects bad reviewer or unsafe output path.

## P156: docs and handoff update

### Documentation tasks

- [ ] Update `docs/local-validation.md` with Level 16 focused commands.
- [ ] Update `docs/next-session-handoff.md` with Level 16 status.
- [ ] Update `NEXT_TODO.md` with Level 16 checkpoint.
- [ ] Add Level 16 generation command.
- [ ] Add Level 16 validation command group.

## P157: Level 16 validation checkpoint

### Commands

```powershell
cd C:\Users\junny\Desktop\traceLeak\TraceLeak
git pull --ff-only
pytest tests/test_level16_pre_handoff_review.py
pytest tests/test_level16_pre_handoff_review_report.py
pytest tests/test_write_level16_files_cli.py
ruff check .
pytest
```

### Completion criteria

- [ ] Focused Level 16 tests pass.
- [ ] `ruff check .` passes.
- [ ] Full `pytest` passes.
- [ ] Level 16 output artifacts stay under `reports/local/`.

## Recommended implementation order

1. P153 pre-handoff review manifest.
2. P154 pre-handoff review report.
3. P155 writer CLI.
4. P156 docs and handoff update.
5. P157 validation checkpoint.

## Stop condition

Stop before Level 17 unless Level 16 focused tests, `ruff check .`, and full `pytest` all pass locally.
