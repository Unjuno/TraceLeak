# Level 20 Completion TODO

Level 20 is final index planning after Level 19.

Current baseline: Level 19 is locally reported all pass. Level 20 remains review-only and path-only.

## Level 20 goal

Create a final path-only index that records Level 19 summary output paths and validation state.

## Level 20 done definition

- [x] A versioned index exists.
- [x] The index records expected Level 19 output paths.
- [x] The index records status as pending local validation by default.
- [x] The index remains review-only and path-only.
- [x] A Markdown report exists.
- [x] A writer CLI exists for Level 20 outputs.
- [ ] Focused Level 20 tests pass.
- [ ] `ruff check .` passes.
- [ ] Full `pytest` passes.

## P173: index

### Status

- [x] Added Level 20 helper.
- [x] Defined `traceleak.level20_closure_index.v1`.
- [x] Recorded expected Level 19 output paths.
- [x] Recorded status as pending local validation.
- [x] Kept review-only and path-only flags.
- [x] Added focused tests.

## P174: report

### Status

- [x] Added Markdown report renderer.
- [x] Rendered status.
- [x] Rendered output paths.
- [x] Rendered review-only boundary.
- [x] Rendered expected validation commands.
- [x] Rendered next-level preconditions.
- [x] Added focused tests.

## P175: Level 20 writer CLI

### Status

- [x] Added writer CLI name: `traceleak-write-level20-files`.
- [x] Built Level 20 index.
- [x] Rendered report.
- [x] Wrote JSON and Markdown under `reports/local/level20_closure_index/`.
- [x] Added focused tests.

## P176: docs and handoff update

### Status

- [x] Updated `docs/local-validation.md` with Level 20 focused commands.
- [x] Updated `docs/next-session-handoff.md` with Level 20 status.
- [x] Updated `NEXT_TODO.md` with Level 20 checkpoint.
- [x] Added Level 20 generation command.
- [x] Added Level 20 validation command group.

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

## Stop condition

Stop before Level 21 unless Level 20 focused tests, `ruff check .`, and full `pytest` all pass locally.
