# Level 19 Completion TODO

Level 19 is final handoff-summary planning after Level 18.

Current baseline: Level 18 is locally reported all pass. Level 19 must remain review-only and path-only.

## Level 19 goal

Create a final handoff-summary layer that references the Level 18 archive index and summarizes the local review chain status.

## Level 19 flow

```text
Level 18 archive index
  -> handoff summary
  -> handoff summary report
  -> writer CLI
  -> validation checkpoint
```

## Level 19 done definition

- [ ] A versioned handoff summary exists.
- [ ] The summary references the Level 18 archive index format.
- [ ] The summary records reviewed levels from 13 through 18.
- [ ] The summary records final local status as pending validation by default.
- [ ] The summary remains review-only and path-only.
- [ ] A handoff-summary Markdown report exists.
- [ ] A writer CLI exists for Level 19 outputs.
- [ ] Focused Level 19 tests pass.
- [ ] `ruff check .` passes.
- [ ] Full `pytest` passes.

## P168: handoff summary

### Purpose

Define a path-only handoff summary over the Level 18 archive index.

### Implementation tasks

- [ ] Add Level 19 handoff-summary helper.
- [ ] Define `traceleak.level19_handoff_summary.v1`.
- [ ] Require a valid Level 18 archive index.
- [ ] Record source index format and phase.
- [ ] Record reviewed levels:
  - [ ] level13.
  - [ ] level14.
  - [ ] level15.
  - [ ] level16.
  - [ ] level17.
  - [ ] level18.
- [ ] Record summary status as pending local validation.
- [ ] Keep review-only and path-only flags.

### Tests

- [ ] Build summary from valid Level 18 index.
- [ ] Reject invalid source index format.
- [ ] Reject content read enabled.
- [ ] Reject command executed enabled.
- [ ] Validate JSON writer.

## P169: handoff-summary report

### Purpose

Render a Markdown report for Level 19 handoff summary.

### Required sections

- [ ] Summary status.
- [ ] Source archive index.
- [ ] Reviewed levels.
- [ ] Review-only boundary.
- [ ] Expected validation commands.
- [ ] Next-level preconditions.

### Tests

- [ ] Report contains required headings.
- [ ] Report states review-only boundary.
- [ ] Report states path-only boundary.
- [ ] Report states no commands were executed.
- [ ] Report states no content was read.

## P170: Level 19 writer CLI

### Purpose

Expose Level 19 handoff-summary output generation.

### Implementation tasks

- [ ] Add writer CLI name.
- [ ] Build Level 19 handoff summary.
- [ ] Render handoff-summary report.
- [ ] Write JSON and Markdown under `reports/local/level19_handoff_summary/`.
- [ ] Do not read output contents.
- [ ] Do not execute validation commands.
- [ ] Do not mutate source trees.

### Tests

- [ ] CLI writes handoff summary.
- [ ] CLI writes handoff-summary report.
- [ ] CLI rejects bad reviewer or unsafe output path.

## P171: docs and handoff update

### Documentation tasks

- [ ] Update `docs/local-validation.md` with Level 19 focused commands.
- [ ] Update `docs/next-session-handoff.md` with Level 19 status.
- [ ] Update `NEXT_TODO.md` with Level 19 checkpoint.
- [ ] Add Level 19 generation command.
- [ ] Add Level 19 validation command group.

## P172: Level 19 validation checkpoint

### Commands

```powershell
cd C:\Users\junny\Desktop\traceLeak\TraceLeak
git pull --ff-only
pytest tests/test_level19_handoff_summary.py
pytest tests/test_level19_handoff_summary_report.py
pytest tests/test_write_level19_files_cli.py
ruff check .
pytest
```

### Completion criteria

- [ ] Focused Level 19 tests pass.
- [ ] `ruff check .` passes.
- [ ] Full `pytest` passes.
- [ ] Level 19 outputs stay under `reports/local/`.

## Recommended implementation order

1. P168 handoff summary.
2. P169 handoff-summary report.
3. P170 writer CLI.
4. P171 docs and handoff update.
5. P172 validation checkpoint.

## Stop condition

Stop before Level 20 unless Level 19 focused tests, `ruff check .`, and full `pytest` all pass locally.
