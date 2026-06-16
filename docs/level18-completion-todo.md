# Level 18 Completion TODO

Level 18 is final archive-index planning after Level 17.

Current baseline: Level 17 is locally reported all pass. Level 18 must remain review-only and path-only.

## Level 18 goal

Create a final archive-index layer that records the set of review-only local artifacts produced by Levels 13 through 17.

The Level 18 flow is:

```text
Level 17 release-readiness artifacts
  -> archive index
  -> archive index report
  -> writer CLI
  -> validation checkpoint
```

## Level 18 non-goals

- No external project build.
- No external project execution.
- No source tree mutation.
- No artifact content parsing.
- No command execution.
- No private material collection.
- No claim generation.

## Level 18 done definition

Level 18 is complete when all of the following are true:

- [ ] A versioned archive index exists.
- [ ] The index records expected artifact families from Levels 13 through 17.
- [ ] The index records artifact paths only.
- [ ] The index records archive status as pending local validation by default.
- [ ] The index remains review-only and path-only.
- [ ] An archive-index Markdown report exists.
- [ ] A writer CLI exists for Level 18 artifacts.
- [ ] Focused Level 18 tests pass.
- [ ] `ruff check .` passes.
- [ ] Full `pytest` passes.

## P163: archive index

### Purpose

Define a path-only archive index for local review artifacts.

### Implementation tasks

- [ ] Add Level 18 archive-index helper.
- [ ] Define `traceleak.level18_archive_index.v1`.
- [ ] Record expected artifact families:
  - [ ] level13_closure.
  - [ ] level14_completeness.
  - [ ] level15_validation_rollup.
  - [ ] level16_review.
  - [ ] level17_release_readiness.
- [ ] Record relative paths only under `reports/local/`.
- [ ] Record archive status as pending local validation.
- [ ] Keep flags:
  - [ ] review only true.
  - [ ] path only true.
  - [ ] content read false.
  - [ ] command executed false.
  - [ ] claim generated false.

### Tests

- [ ] Build default archive index.
- [ ] Reject absolute paths.
- [ ] Reject parent-directory paths.
- [ ] Reject content read enabled.
- [ ] Reject command executed enabled.
- [ ] Validate JSON writer.

## P164: archive-index report

### Purpose

Render a Markdown report for Level 18 archive index.

### Required sections

- [ ] Archive status.
- [ ] Artifact families.
- [ ] Path-only inventory.
- [ ] Review-only boundary.
- [ ] Expected validation commands.
- [ ] Next-level preconditions.

### Tests

- [ ] Report contains required headings.
- [ ] Report states review-only boundary.
- [ ] Report states no commands were executed.
- [ ] Report states no content was read.
- [ ] Report states no claim was generated.

## P165: Level 18 writer CLI

### Purpose

Expose Level 18 archive-index artifact generation.

### Implementation tasks

- [ ] Add neutral writer CLI name.
- [ ] Build Level 18 archive index.
- [ ] Render archive-index report.
- [ ] Write JSON and Markdown under `reports/local/level18_archive_index/`.
- [ ] Do not read artifact contents.
- [ ] Do not execute validation commands.
- [ ] Do not mutate source trees.
- [ ] Do not generate claims.

### Tests

- [ ] CLI writes archive index.
- [ ] CLI writes archive-index report.
- [ ] CLI rejects bad reviewer or unsafe output path.

## P166: docs and handoff update

### Documentation tasks

- [ ] Update `docs/local-validation.md` with Level 18 focused commands.
- [ ] Update `docs/next-session-handoff.md` with Level 18 status.
- [ ] Update `NEXT_TODO.md` with Level 18 checkpoint.
- [ ] Add Level 18 generation command.
- [ ] Add Level 18 validation command group.

## P167: Level 18 validation checkpoint

### Commands

```powershell
cd C:\Users\junny\Desktop\traceLeak\TraceLeak
git pull --ff-only
pytest tests/test_level18_archive_index.py
pytest tests/test_level18_archive_index_report.py
pytest tests/test_write_level18_files_cli.py
ruff check .
pytest
```

### Completion criteria

- [ ] Focused Level 18 tests pass.
- [ ] `ruff check .` passes.
- [ ] Full `pytest` passes.
- [ ] Level 18 output artifacts stay under `reports/local/`.

## Recommended implementation order

1. P163 archive index.
2. P164 archive-index report.
3. P165 writer CLI.
4. P166 docs and handoff update.
5. P167 validation checkpoint.

## Stop condition

Stop before Level 19 unless Level 18 focused tests, `ruff check .`, and full `pytest` all pass locally.
