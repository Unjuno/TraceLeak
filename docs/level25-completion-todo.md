# Level 25 Completion TODO

Level 25 is path-index planning after Level 24.

Current baseline: Level 24 is locally reported all pass. Level 25 remains review-only and path-only.

## Level 25 goal

Create a path-only index for Level 24 output paths.

## Level 25 done definition

- [ ] A versioned index exists.
- [ ] The index records expected Level 24 output paths.
- [ ] The index records status as pending local validation by default.
- [ ] The index remains review-only and path-only.
- [ ] A Markdown report exists.
- [ ] A writer CLI exists for Level 25 outputs.
- [ ] Focused Level 25 tests pass.
- [ ] `ruff check .` passes.
- [ ] Full `pytest` passes.

## P198: index

### Tasks

- [ ] Add Level 25 index helper.
- [ ] Define `traceleak.level25_index.v1`.
- [ ] Record expected Level 24 output paths.
- [ ] Record status as pending local validation.
- [ ] Keep review-only and path-only flags.
- [ ] Add focused tests.

## P199: report

### Tasks

- [ ] Add Markdown report renderer.
- [ ] Render status.
- [ ] Render output paths.
- [ ] Render review-only boundary.
- [ ] Render expected validation commands.
- [ ] Add focused tests.

## P200: writer CLI

### Tasks

- [ ] Add writer CLI name.
- [ ] Build Level 25 index.
- [ ] Render report.
- [ ] Write JSON and Markdown under `reports/local/level25_index/`.
- [ ] Add focused tests.

## P201: docs and handoff update

### Tasks

- [ ] Update `docs/local-validation.md` with Level 25 focused commands.
- [ ] Update `docs/next-session-handoff.md` with Level 25 status.
- [ ] Update `NEXT_TODO.md` with Level 25 checkpoint.
- [ ] Add Level 25 generation command.
- [ ] Add Level 25 validation command group.

## P202: Level 25 validation checkpoint

### Commands

```powershell
cd C:\Users\junny\Desktop\traceLeak\TraceLeak
git pull --ff-only
pytest tests/test_level25_index.py
pytest tests/test_level25_index_report.py
pytest tests/test_write_level25_files_cli.py
ruff check .
pytest
```

### Completion criteria

- [ ] Focused Level 25 tests pass.
- [ ] `ruff check .` passes.
- [ ] Full `pytest` passes.
- [ ] Level 25 outputs stay under `reports/local/`.

## Stop condition

Stop before Level 26 unless Level 25 focused tests, `ruff check .`, and full `pytest` all pass locally.
