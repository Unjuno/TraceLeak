# Level 21 Completion TODO

Level 21 is final status-index planning after Level 20.

Current baseline: Level 20 is locally reported all pass. Level 21 must remain review-only and path-only.

## Level 21 goal

Create a final status-index layer that records Level 20 output paths and the local validation boundary for a later checkpoint.

## Level 21 flow

```text
Level 20 outputs
  -> status index
  -> status index report
  -> writer CLI
  -> validation checkpoint
```

## Level 21 done definition

- [ ] A versioned status index exists.
- [ ] The index records expected Level 20 output paths.
- [ ] The index records status as pending local validation by default.
- [ ] The index remains review-only and path-only.
- [ ] A Markdown report exists.
- [ ] A writer CLI exists for Level 21 outputs.
- [ ] Focused Level 21 tests pass.
- [ ] `ruff check .` passes.
- [ ] Full `pytest` passes.

## P178: status index

### Purpose

Define a path-only status index over Level 20 outputs.

### Implementation tasks

- [ ] Add Level 21 status-index helper.
- [ ] Define `traceleak.level21_status_index.v1`.
- [ ] Record expected Level 20 output paths:
  - [ ] `reports/local/level20_closure_index/level20-closure-index.json`.
  - [ ] `reports/local/level20_closure_index/level20-closure-index-report.md`.
- [ ] Record status as pending local validation.
- [ ] Keep review-only and path-only flags.

### Tests

- [ ] Build default status index.
- [ ] Reject absolute paths.
- [ ] Reject parent-directory paths.
- [ ] Reject content read enabled.
- [ ] Reject command executed enabled.
- [ ] Validate JSON writer.

## P179: status-index report

### Purpose

Render a Markdown report for Level 21 status index.

### Required sections

- [ ] Status.
- [ ] Output paths.
- [ ] Review-only boundary.
- [ ] Expected validation commands.
- [ ] Next-level preconditions.

### Tests

- [ ] Report contains required headings.
- [ ] Report states review-only boundary.
- [ ] Report states path-only boundary.
- [ ] Report states no commands were executed.
- [ ] Report states no content was read.

## P180: Level 21 writer CLI

### Purpose

Expose Level 21 status-index output generation.

### Implementation tasks

- [ ] Add writer CLI name.
- [ ] Build Level 21 status index.
- [ ] Render status-index report.
- [ ] Write JSON and Markdown under `reports/local/level21_status_index/`.
- [ ] Do not read output contents.
- [ ] Do not execute validation commands.
- [ ] Do not mutate source trees.

### Tests

- [ ] CLI writes status index.
- [ ] CLI writes status-index report.
- [ ] CLI rejects bad reviewer or unsafe output path.

## P181: docs and handoff update

### Documentation tasks

- [ ] Update `docs/local-validation.md` with Level 21 focused commands.
- [ ] Update `docs/next-session-handoff.md` with Level 21 status.
- [ ] Update `NEXT_TODO.md` with Level 21 checkpoint.
- [ ] Add Level 21 generation command.
- [ ] Add Level 21 validation command group.

## P182: Level 21 validation checkpoint

### Commands

```powershell
cd C:\Users\junny\Desktop\traceLeak\TraceLeak
git pull --ff-only
pytest tests/test_level21_status_index.py
pytest tests/test_level21_status_index_report.py
pytest tests/test_write_level21_files_cli.py
ruff check .
pytest
```

### Completion criteria

- [ ] Focused Level 21 tests pass.
- [ ] `ruff check .` passes.
- [ ] Full `pytest` passes.
- [ ] Level 21 outputs stay under `reports/local/`.

## Recommended implementation order

1. P178 status index.
2. P179 status-index report.
3. P180 writer CLI.
4. P181 docs and handoff update.
5. P182 validation checkpoint.

## Stop condition

Stop before Level 22 unless Level 21 focused tests, `ruff check .`, and full `pytest` all pass locally.
