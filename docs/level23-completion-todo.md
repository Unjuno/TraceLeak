# Level 23 Completion TODO

Level 23 is path-index planning after Level 22.

Current baseline: Level 22 is locally reported all pass. Level 23 remains review-only and path-only.

## Level 23 goal

Create a path-only index for Level 22 output paths.

## Level 23 done definition

- [ ] A versioned index exists.
- [ ] The index records expected Level 22 output paths.
- [ ] The index records status as pending local validation by default.
- [ ] The index remains review-only and path-only.
- [ ] A Markdown report exists.
- [ ] A writer CLI exists for Level 23 outputs.
- [ ] Focused Level 23 tests pass.
- [ ] `ruff check .` passes.
- [ ] Full `pytest` passes.

## P188: index

### Tasks

- [ ] Add Level 23 index helper.
- [ ] Define `traceleak.level23_index.v1`.
- [ ] Record expected Level 22 output paths.
- [ ] Record status as pending local validation.
- [ ] Keep review-only and path-only flags.
- [ ] Add focused tests.

## P189: report

### Tasks

- [ ] Add Markdown report renderer.
- [ ] Render status.
- [ ] Render output paths.
- [ ] Render review-only boundary.
- [ ] Render expected validation commands.
- [ ] Add focused tests.

## P190: writer CLI

### Tasks

- [ ] Add writer CLI name.
- [ ] Build Level 23 index.
- [ ] Render report.
- [ ] Write JSON and Markdown under `reports/local/level23_index/`.
- [ ] Add focused tests.

## P191: docs and handoff update

### Tasks

- [ ] Update `docs/local-validation.md` with Level 23 focused commands.
- [ ] Update `docs/next-session-handoff.md` with Level 23 status.
- [ ] Update `NEXT_TODO.md` with Level 23 checkpoint.
- [ ] Add Level 23 generation command.
- [ ] Add Level 23 validation command group.

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
