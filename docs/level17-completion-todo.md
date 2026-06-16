# Level 17 Completion TODO

Level 17 is release-readiness checklist planning after Level 16.

Current baseline: Level 16 is locally reported all pass. Level 17 must remain review-only and path-only.

## Level 17 goal

Create a release-readiness checklist layer that summarizes whether prior local review artifacts are ready for a later release-style handoff.

The Level 17 flow is:

```text
Level 16 review artifacts
  -> release-readiness checklist
  -> release-readiness report
  -> writer CLI
  -> validation checkpoint
```

## Level 17 non-goals

- No external project build.
- No external project execution.
- No source tree mutation.
- No artifact content parsing.
- No command execution.
- No private material collection.
- No claim generation.

## Level 17 done definition

Level 17 is complete when all of the following are true:

- [ ] A versioned release-readiness checklist exists.
- [ ] The checklist requires a valid Level 16 review artifact.
- [ ] The checklist records review disposition.
- [ ] The checklist records expected validation commands.
- [ ] The checklist records readiness items with pending local validation by default.
- [ ] The checklist remains review-only and path-only.
- [ ] A release-readiness Markdown report exists.
- [ ] A writer CLI exists for Level 17 artifacts.
- [ ] Focused Level 17 tests pass.
- [ ] `ruff check .` passes.
- [ ] Full `pytest` passes.

## P158: release-readiness checklist

### Purpose

Define a release-readiness checklist over Level 16 review artifacts.

### Implementation tasks

- [ ] Add Level 17 release-readiness helper.
- [ ] Define `traceleak.level17_release_readiness.v1`.
- [ ] Require a valid Level 16 review artifact.
- [ ] Record source review format and phase.
- [ ] Record review disposition.
- [ ] Record expected validation commands.
- [ ] Record readiness items:
  - [ ] focused tests pending.
  - [ ] ruff pending.
  - [ ] full pytest pending.
  - [ ] docs updated pending.
- [ ] Keep flags:
  - [ ] review only true.
  - [ ] path only true.
  - [ ] content read false.
  - [ ] command executed false.
  - [ ] claim generated false.

### Tests

- [ ] Build checklist from valid Level 16 review.
- [ ] Reject invalid source review format.
- [ ] Reject content read enabled.
- [ ] Reject command executed enabled.
- [ ] Reject claim generated enabled.
- [ ] Validate JSON writer.

## P159: release-readiness report

### Purpose

Render a Markdown report for Level 17 release-readiness checklist.

### Required sections

- [ ] Readiness status.
- [ ] Source review disposition.
- [ ] Readiness items.
- [ ] Expected validation commands.
- [ ] Review-only boundary.
- [ ] Next-level preconditions.

### Tests

- [ ] Report contains required headings.
- [ ] Report states review-only boundary.
- [ ] Report states no commands were executed.
- [ ] Report states no content was read.
- [ ] Report states no claim was generated.

## P160: Level 17 writer CLI

### Purpose

Expose Level 17 release-readiness artifact generation.

### Implementation tasks

- [ ] Add neutral writer CLI name.
- [ ] Build Level 17 release-readiness checklist.
- [ ] Render release-readiness report.
- [ ] Write JSON and Markdown under `reports/local/level17_release_readiness/`.
- [ ] Do not read artifact contents.
- [ ] Do not execute validation commands.
- [ ] Do not mutate source trees.
- [ ] Do not generate claims.

### Tests

- [ ] CLI writes release-readiness checklist.
- [ ] CLI writes release-readiness report.
- [ ] CLI rejects bad reviewer or unsafe output path.

## P161: docs and handoff update

### Documentation tasks

- [ ] Update `docs/local-validation.md` with Level 17 focused commands.
- [ ] Update `docs/next-session-handoff.md` with Level 17 status.
- [ ] Update `NEXT_TODO.md` with Level 17 checkpoint.
- [ ] Add Level 17 generation command.
- [ ] Add Level 17 validation command group.

## P162: Level 17 validation checkpoint

### Commands

```powershell
cd C:\Users\junny\Desktop\traceLeak\TraceLeak
git pull --ff-only
pytest tests/test_level17_release_readiness.py
pytest tests/test_level17_release_readiness_report.py
pytest tests/test_write_level17_files_cli.py
ruff check .
pytest
```

### Completion criteria

- [ ] Focused Level 17 tests pass.
- [ ] `ruff check .` passes.
- [ ] Full `pytest` passes.
- [ ] Level 17 output artifacts stay under `reports/local/`.

## Recommended implementation order

1. P158 release-readiness checklist.
2. P159 release-readiness report.
3. P160 writer CLI.
4. P161 docs and handoff update.
5. P162 validation checkpoint.

## Stop condition

Stop before Level 18 unless Level 17 focused tests, `ruff check .`, and full `pytest` all pass locally.
