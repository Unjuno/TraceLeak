# Level 22 Completion TODO

Level 22 is status planning after Level 21.

Current baseline: Level 21 is locally reported all pass. Level 22 remains review-only and path-only.

## Level 22 goal

Create a path-only index for Level 21 output paths.

## Level 22 done definition

- [ ] A versioned index exists.
- [ ] The index records expected Level 21 output paths.
- [ ] The index records status as pending local validation by default.
- [ ] The index remains review-only and path-only.
- [ ] A Markdown report exists.
- [ ] A writer CLI exists for Level 22 outputs.
- [ ] Focused Level 22 tests pass.
- [ ] `ruff check .` passes.
- [ ] Full `pytest` passes.

## P183: index

### Tasks

- [ ] Add Level 22 index helper.
- [ ] Define `traceleak.level22_index.v1`.
- [ ] Record expected Level 21 output paths.
- [ ] Record status as pending local validation.
- [ ] Keep review-only and path-only flags.
- [ ] Add focused tests.

## P184: report

### Tasks

- [ ] Add Markdown report renderer.
- [ ] Render status.
- [ ] Render output paths.
- [ ] Render review-only boundary.
- [ ] Render expected validation commands.
- [ ] Add focused tests.

## P185: writer CLI

### Tasks

- [ ] Add writer CLI name.
- [ ] Build Level 22 index.
- [ ] Render report.
- [ ] Write JSON and Markdown under `reports/local/level22_index/`.
- [ ] Add focused tests.

## P186: docs and handoff update

### Tasks

- [ ] Update `docs/local-validation.md` with Level 22 focused commands.
- [ ] Update `docs/next-session-handoff.md` with Level 22 status.
- [ ] Update `NEXT_TODO.md` with Level 22 checkpoint.
- [ ] Add Level 22 generation command.
- [ ] Add Level 22 validation command group.

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
