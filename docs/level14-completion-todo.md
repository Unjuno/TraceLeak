# Level 14 Completion TODO

Level 14 is handoff completeness audit planning after Level 13.

Current baseline: Level 13 is locally reported all pass. Level 14 must remain review-only and path-only. It may audit Level 13 handoff inventory metadata, but it must not parse artifact contents or widen behavior.

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

- [ ] A versioned completeness audit exists.
- [ ] The audit requires a valid Level 13 handoff inventory.
- [ ] The audit records family count and path count.
- [ ] The audit records missing family names when required families are absent.
- [ ] The audit remains path-only.
- [ ] A completeness Markdown report exists.
- [ ] A writer CLI exists for Level 14 completeness artifacts.
- [ ] Focused Level 14 tests pass.
- [ ] `ruff check .` passes.
- [ ] Full `pytest` passes.

## P143: completeness audit

### Purpose

Define a completeness audit over the Level 13 handoff inventory.

### Implementation tasks

- [ ] Add Level 14 completeness audit helper.
- [ ] Define `traceleak.level14_completeness_audit.v1`.
- [ ] Require a valid Level 13 handoff inventory.
- [ ] Record source inventory format and phase.
- [ ] Record family count.
- [ ] Record total path count.
- [ ] Record required families:
  - [ ] `level6_profile`
  - [ ] `level7_planning`
  - [ ] `level8_intake`
  - [ ] `level9_readiness`
  - [ ] `level10_review`
  - [ ] `level11_next_todo`
  - [ ] `level12_checkpoint`
- [ ] Record missing required families.
- [ ] Record completeness status:
  - [ ] `complete` when no required family is missing.
  - [ ] `incomplete` otherwise.
- [ ] Keep flags:
  - [ ] path only true.
  - [ ] content read false.
  - [ ] claim generated false.

### Tests

- [ ] Build audit from complete inventory.
- [ ] Build audit from incomplete inventory.
- [ ] Reject invalid inventory linkage.
- [ ] Reject content read enabled.
- [ ] Reject claim generated enabled.
- [ ] Validate JSON writer.

## P144: completeness report

### Purpose

Render a Markdown report for Level 14 handoff completeness.

### Required sections

- [ ] Completeness status.
- [ ] Required families.
- [ ] Missing families.
- [ ] Handoff family counts.
- [ ] Path-only boundary.
- [ ] Local validation commands.

### Tests

- [ ] Report contains required headings.
- [ ] Report states path-only boundary.
- [ ] Report states no content was read.
- [ ] Report states no claim was generated.

## P145: Level 14 writer CLI

### Purpose

Expose Level 14 completeness artifact generation.

### Implementation tasks

- [ ] Add neutral writer CLI name.
- [ ] Build Level 13 closure artifacts.
- [ ] Build Level 14 completeness audit.
- [ ] Render completeness report.
- [ ] Write JSON and Markdown under `reports/local/level14_completeness/`.
- [ ] Do not read artifact contents.
- [ ] Do not execute external commands.
- [ ] Do not mutate source trees.
- [ ] Do not generate claims.

### Tests

- [ ] CLI writes completeness audit.
- [ ] CLI writes completeness report.
- [ ] CLI rejects bad reviewer or unsafe output path.

## P146: docs and handoff update

### Documentation tasks

- [ ] Update `docs/local-validation.md` with Level 14 focused commands.
- [ ] Update `docs/next-session-handoff.md` with Level 14 status.
- [ ] Update `NEXT_TODO.md` with Level 14 checkpoint.
- [ ] Add Level 14 generation command.
- [ ] Add Level 14 validation command group.

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

## Recommended implementation order

1. P143 completeness audit.
2. P144 completeness report.
3. P145 writer CLI.
4. P146 docs and handoff update.
5. P147 validation checkpoint.

## Stop condition

Stop before Level 15 unless Level 14 focused tests, `ruff check .`, and full `pytest` all pass locally.
