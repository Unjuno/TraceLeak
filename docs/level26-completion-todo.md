# Level 26 Completion TODO

Level 26 is path-index planning after Level 25.

Current baseline: Level 25 is locally reported all pass. Level 26 remains review-only and path-only.

## Level 26 goal

Create a path-only index for Level 25 output paths.

## Level 26 done definition

- [ ] A versioned index exists.
- [ ] The index records expected Level 25 output paths.
- [ ] The index records status as pending local validation by default.
- [ ] The index remains review-only and path-only.
- [ ] A Markdown report exists.
- [ ] A writer CLI exists for Level 26 outputs.
- [ ] Focused Level 26 tests pass.
- [ ] `ruff check .` passes.
- [ ] Full `pytest` passes.

## P203: index

### Tasks

- [ ] Add Level 26 index helper.
- [ ] Define `traceleak.level26_index.v1`.
- [ ] Record expected Level 25 output paths.
- [ ] Record status as pending local validation.
- [ ] Keep review-only and path-only flags.
- [ ] Add focused tests.

## P204: report

### Tasks

- [ ] Add Markdown report renderer.
- [ ] Render status.
- [ ] Render output paths.
- [ ] Render expected validation commands.
- [ ] Add focused tests.

## P205: writer CLI

### Tasks

- [ ] Add writer CLI name.
- [ ] Build Level 26 index.
- [ ] Render report.
- [ ] Write JSON and Markdown under `reports/local/level26_index/`.
- [ ] Add focused tests.

## P206: docs and handoff update

### Tasks

- [ ] Update `docs/next-session-handoff.md` with Level 26 status.
- [ ] Update `NEXT_TODO.md` with Level 26 checkpoint.
- [ ] Add Level 26 generation command.
- [ ] Add Level 26 validation command group.

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
