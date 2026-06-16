# Level 20 Completion TODO

Level 20 is final closure-index planning after Level 19.

Current baseline: Level 19 is locally reported all pass. Level 20 must remain review-only and path-only.

## Level 20 goal

Create a final closure-index layer that records the Level 19 summary output paths and the validation boundary for a later closing checkpoint.

## Level 20 flow

```text
Level 19 summary outputs
  -> closure index
  -> closure index report
  -> writer CLI
  -> validation checkpoint
```

## Level 20 done definition

- [ ] A versioned closure index exists.
- [ ] The index records expected Level 19 output paths.
- [ ] The index records closure status as pending local validation by default.
- [ ] The index remains review-only and path-only.
- [ ] A closure-index Markdown report exists.
- [ ] A writer CLI exists for Level 20 outputs.
- [ ] Focused Level 20 tests pass.
- [ ] `ruff check .` passes.
- [ ] Full `pytest` passes.

## P173: closure index

### Purpose

Define a path-only closure index over Level 19 outputs.

### Implementation tasks

- [ ] Add Level 20 closure-index helper.
- [ ] Define `traceleak.level20_closure_index.v1`.
- [ ] Record expected Level 19 output paths:
  - [ ] `reports/local/level19_handoff_summary/level19-summary.json`.
  - [ ] `reports/local/level19_handoff_summary/level19-summary-report.md`.
- [ ] Record closure status as pending local validation.
- [ ] Keep review-only and path-only flags.

### Tests

- [ ] Build default closure index.
- [ ] Reject absolute paths.
- [ ] Reject parent-directory paths.
- [ ] Reject content read enabled.
- [ ] Reject command executed enabled.
- [ ] Validate JSON writer.

## P174: closure-index report

### Purpose

Render a Markdown report for Level 20 closure index.

### Required sections

- [ ] Closure status.
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

## P175: Level 20 writer CLI

### Purpose

Expose Level 20 closure-index output generation.

### Implementation tasks

- [ ] Add writer CLI name.
- [ ] Build Level 20 closure index.
- [ ] Render closure-index report.
- [ ] Write JSON and Markdown under `reports/local/level20_closure_index/`.
- [ ] Do not read output contents.
- [ ] Do not execute validation commands.
- [ ] Do not mutate source trees.

### Tests

- [ ] CLI writes closure index.
- [ ] CLI writes closure-index report.
- [ ] CLI rejects bad reviewer or unsafe output path.

## P176: docs and handoff update

### Documentation tasks

- [ ] Update `docs/local-validation.md` with Level 20 focused commands.
- [ ] Update `docs/next-session-handoff.md` with Level 20 status.
- [ ] Update `NEXT_TODO.md` with Level 20 checkpoint.
- [ ] Add Level 20 generation command.
- [ ] Add Level 20 validation command group.

## P177: Level 20 validation checkpoint

### Commands

```powershell
cd C:\Users\junny\Desktop\traceLeak\TraceLeak
git pull --ff-only
pytest tests/test_level20_closure_index.py
pytest tests/test_level20_closure_index_report.py
pytest tests/test_write_level20_files_cli.py
ruff check .
pytest
```

### Completion criteria

- [ ] Focused Level 20 tests pass.
- [ ] `ruff check .` passes.
- [ ] Full `pytest` passes.
- [ ] Level 20 outputs stay under `reports/local/`.

## Recommended implementation order

1. P173 closure index.
2. P174 closure-index report.
3. P175 writer CLI.
4. P176 docs and handoff update.
5. P177 validation checkpoint.

## Stop condition

Stop before Level 21 unless Level 20 focused tests, `ruff check .`, and full `pytest` all pass locally.
