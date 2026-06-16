# Level 22 Completion TODO

Level 22 is status planning after Level 21.

Current baseline: Level 21 is locally reported all pass. Level 22 remains review-only and path-only.

## Level 22 goal

Create a path-only index for Level 21 output paths.

## Level 22 done definition

- [x] A versioned index exists.
- [x] The index records expected Level 21 output paths.
- [x] The index records status as pending local validation by default.
- [x] The index remains review-only and path-only.
- [x] A Markdown report exists.
- [x] A writer CLI exists for Level 22 outputs.
- [ ] Focused Level 22 tests pass.
- [ ] `ruff check .` passes.
- [ ] Full `pytest` passes.

## P183: index

### Status

- [x] Added Level 22 index helper.
- [x] Defined `traceleak.level22_index.v1`.
- [x] Recorded expected Level 21 output paths.
- [x] Recorded status as pending local validation.
- [x] Kept review-only and path-only flags.
- [x] Added focused tests.

## P184: report

### Status

- [x] Added Markdown report renderer.
- [x] Rendered status.
- [x] Rendered output paths.
- [x] Rendered review-only boundary.
- [x] Rendered expected validation commands.
- [x] Added focused tests.

## P185: writer CLI

### Status

- [x] Added writer CLI name: `traceleak-write-level22-files`.
- [x] Built Level 22 index.
- [x] Rendered report.
- [x] Wrote JSON and Markdown under `reports/local/level22_index/`.
- [x] Added focused tests.

## P186: docs and handoff update

### Status

- [x] Updated `docs/local-validation.md` with Level 22 focused commands.
- [x] Updated `docs/next-session-handoff.md` with Level 22 status.
- [x] Updated `NEXT_TODO.md` with Level 22 checkpoint.
- [x] Added Level 22 generation command.
- [x] Added Level 22 validation command group.

## P187: Level 22 validation checkpoint

### Commands

```powershell
cd C:\Users\junny\Desktop\traceLeak\TraceLeak
git pull --ff-only
pytest tests/test_level22_index.py
pytest tests/test_level22_index_report.py
pytest tests/test_write_level22_files_cli.py
ruff check .
pytest
```

### Completion criteria

- [ ] Focused Level 22 tests pass.
- [ ] `ruff check .` passes.
- [ ] Full `pytest` passes.
- [ ] Level 22 outputs stay under `reports/local/`.

## Stop condition

Stop before Level 23 unless Level 22 focused tests, `ruff check .`, and full `pytest` all pass locally.
