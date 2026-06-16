# Level 23 Completion TODO

Level 23 is path-index planning after Level 22.

Current baseline: Level 22 is locally reported all pass. Level 23 remains review-only and path-only.

## Level 23 goal

Create a path-only index for Level 22 output paths.

## Level 23 done definition

- [x] A versioned index exists.
- [x] The index records expected Level 22 output paths.
- [x] The index records status as pending local validation by default.
- [x] The index remains review-only and path-only.
- [x] A Markdown report exists.
- [x] A writer CLI exists for Level 23 outputs.
- [ ] Focused Level 23 tests pass.
- [ ] `ruff check .` passes.
- [ ] Full `pytest` passes.

## P188: index

### Status

- [x] Added Level 23 index helper.
- [x] Defined `traceleak.level23_index.v1`.
- [x] Recorded expected Level 22 output paths.
- [x] Recorded status as pending local validation.
- [x] Kept review-only and path-only flags.
- [x] Added focused tests.

## P189: report

### Status

- [x] Added Markdown report renderer.
- [x] Rendered status.
- [x] Rendered output paths.
- [x] Rendered review-only boundary.
- [x] Rendered expected validation commands.
- [x] Added focused tests.

## P190: writer CLI

### Status

- [x] Added writer CLI name: `traceleak-write-level23-files`.
- [x] Built Level 23 index.
- [x] Rendered report.
- [x] Wrote JSON and Markdown under `reports/local/level23_index/`.
- [x] Added focused tests.

## P191: docs and handoff update

### Status

- [x] Updated `docs/local-validation.md` with Level 23 focused commands.
- [x] Updated `docs/next-session-handoff.md` with Level 23 status.
- [x] Updated `NEXT_TODO.md` with Level 23 checkpoint.
- [x] Added Level 23 generation command.
- [x] Added Level 23 validation command group.

## P192: Level 23 validation checkpoint

### Commands

```powershell
cd C:\Users\junny\Desktop\traceLeak\TraceLeak
git pull --ff-only
pytest tests/test_level23_index.py
pytest tests/test_level23_index_report.py
pytest tests/test_write_level23_files_cli.py
ruff check .
pytest
```

### Completion criteria

- [ ] Focused Level 23 tests pass.
- [ ] `ruff check .` passes.
- [ ] Full `pytest` passes.
- [ ] Level 23 outputs stay under `reports/local/`.

## Stop condition

Stop before Level 24 unless Level 23 focused tests, `ruff check .`, and full `pytest` all pass locally.
