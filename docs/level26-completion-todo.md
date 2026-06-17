# Level 26 Completion TODO

Level 26 is path-index planning after Level 25.

Current baseline: Level 25 is locally reported all pass. Level 26 remains review-only and path-only.

## Level 26 goal

Create a path-only index for Level 25 output paths.

## Level 26 done definition

- [x] A versioned index exists.
- [x] The index records expected Level 25 output paths.
- [x] The index records status as pending local validation by default.
- [x] The index remains review-only and path-only.
- [x] A Markdown report exists.
- [x] A writer CLI exists for Level 26 outputs.
- [ ] Focused Level 26 tests pass.
- [ ] `ruff check .` passes.
- [ ] Full `pytest` passes.

## P203: index

### Status

- [x] Added Level 26 index helper.
- [x] Defined `traceleak.level26_index.v1`.
- [x] Recorded expected Level 25 output paths.
- [x] Recorded status as pending local validation.
- [x] Kept review-only and path-only flags.
- [x] Added focused tests.

## P204: report

### Status

- [x] Added Markdown report renderer.
- [x] Rendered status.
- [x] Rendered output paths.
- [x] Rendered expected validation commands.
- [x] Added focused tests.

## P205: writer CLI

### Status

- [x] Added writer CLI name: `traceleak-write-level26-files`.
- [x] Built Level 26 index.
- [x] Rendered report.
- [x] Wrote JSON and Markdown under `reports/local/level26_index/`.
- [x] Added focused tests.

## P206: docs and handoff update

### Status

- [x] Updated `docs/next-session-handoff.md` with Level 26 status.
- [x] Updated `NEXT_TODO.md` with Level 26 checkpoint.
- [x] Added Level 26 generation command.
- [x] Added Level 26 validation command group.

## P207: Level 26 validation checkpoint

### Commands

```powershell
cd C:\Users\junny\Desktop\traceLeak\TraceLeak
git pull --ff-only
pytest tests/test_level26_index.py
pytest tests/test_level26_index_report.py
pytest tests/test_write_level26_files_cli.py
ruff check .
pytest
```

### Completion criteria

- [ ] Focused Level 26 tests pass.
- [ ] `ruff check .` passes.
- [ ] Full `pytest` passes.
- [ ] Level 26 outputs stay under `reports/local/`.

## Stop condition

Stop before Level 27 unless Level 26 focused tests, `ruff check .`, and full `pytest` all pass locally.
