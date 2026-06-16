# Level 24 Completion TODO

Level 24 is path-index planning after Level 23.

Current baseline: Level 23 is locally reported all pass. Level 24 remains review-only and path-only.

## Level 24 goal

Create a path-only index for Level 23 output paths.

## Level 24 done definition

- [ ] A versioned index exists.
- [ ] The index records expected Level 23 output paths.
- [ ] The index records status as pending local validation by default.
- [ ] The index remains review-only and path-only.
- [ ] A Markdown report exists.
- [ ] A writer CLI exists for Level 24 outputs.
- [ ] Focused Level 24 tests pass.
- [ ] `ruff check .` passes.
- [ ] Full `pytest` passes.

## P193: index

### Tasks

- [ ] Add Level 24 index helper.
- [ ] Define `traceleak.level24_index.v1`.
- [ ] Record expected Level 23 output paths.
- [ ] Record status as pending local validation.
- [ ] Keep review-only and path-only flags.
- [ ] Add focused tests.

## P194: report

### Tasks

- [ ] Add Markdown report renderer.
- [ ] Render status.
- [ ] Render output paths.
- [ ] Render review-only boundary.
- [ ] Render expected validation commands.
- [ ] Add focused tests.

## P195: writer CLI

### Tasks

- [ ] Add writer CLI name.
- [ ] Build Level 24 index.
- [ ] Render report.
- [ ] Write JSON and Markdown under `reports/local/level24_index/`.
- [ ] Add focused tests.

## P196: docs and handoff update

### Tasks

- [ ] Update `docs/local-validation.md` with Level 24 focused commands.
- [ ] Update `docs/next-session-handoff.md` with Level 24 status.
- [ ] Update `NEXT_TODO.md` with Level 24 checkpoint.
- [ ] Add Level 24 generation command.
- [ ] Add Level 24 validation command group.

## P197: Level 24 validation checkpoint

### Commands

```powershell
cd C:\Users\junny\Desktop\traceLeak\TraceLeak
git pull --ff-only
pytest tests/test_level24_index.py
pytest tests/test_level24_index_report.py
pytest tests/test_write_level24_files_cli.py
ruff check .
pytest
```

### Completion criteria

- [ ] Focused Level 24 tests pass.
- [ ] `ruff check .` passes.
- [ ] Full `pytest` passes.
- [ ] Level 24 outputs stay under `reports/local/`.

## Stop condition

Stop before Level 25 unless Level 24 focused tests, `ruff check .`, and full `pytest` all pass locally.
