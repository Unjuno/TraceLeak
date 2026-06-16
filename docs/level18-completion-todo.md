# Level 18 Completion TODO

Level 18 is archive-index planning after Level 17.

Current baseline: Level 17 is locally reported all pass. Level 18 remains review-only and path-only.

## Level 18 goal

Create a path-only index for local review outputs produced by Levels 13 through 17.

## Level 18 flow

```text
Level 17 release-readiness outputs
  -> archive index
  -> archive index report
  -> writer CLI
  -> validation checkpoint
```

## Level 18 done definition

- [x] A versioned archive index exists.
- [x] The index records expected output families from Levels 13 through 17.
- [x] The index records relative paths only.
- [x] The index records archive status as pending local validation by default.
- [x] The index remains review-only and path-only.
- [x] An archive-index Markdown report exists.
- [x] A writer CLI exists for Level 18 outputs.
- [ ] Focused Level 18 tests pass.
- [ ] `ruff check .` passes.
- [ ] Full `pytest` passes.

## P163: archive index

### Status

- [x] Added Level 18 archive-index helper.
- [x] Defined `traceleak.level18_archive_index.v1`.
- [x] Recorded expected output families:
  - [x] level13_closure.
  - [x] level14_completeness.
  - [x] level15_validation_rollup.
  - [x] level16_review.
  - [x] level17_release_readiness.
- [x] Recorded relative paths only under `reports/local/`.
- [x] Recorded archive status as pending local validation.
- [x] Kept review-only and path-only flags.
- [x] Added focused tests.

## P164: archive-index report

### Status

- [x] Added Markdown report renderer.
- [x] Rendered archive status.
- [x] Rendered output families.
- [x] Rendered path-only inventory.
- [x] Rendered review-only boundary.
- [x] Rendered expected validation commands.
- [x] Rendered next-level preconditions.
- [x] Added focused tests.

## P165: Level 18 writer CLI

### Status

- [x] Added writer CLI name: `traceleak-write-level18-files`.
- [x] Built Level 18 archive index.
- [x] Rendered archive-index report.
- [x] Wrote JSON and Markdown under `reports/local/level18_archive_index/`.
- [x] Added focused tests.

## P166: docs and handoff update

### Status

- [x] Updated `docs/local-validation.md` with Level 18 focused commands.
- [x] Updated `docs/next-session-handoff.md` with Level 18 status.
- [x] Updated `NEXT_TODO.md` with Level 18 checkpoint.
- [x] Added Level 18 generation command.
- [x] Added Level 18 validation command group.

## P167: Level 18 validation checkpoint

### Commands

```powershell
cd C:\Users\junny\Desktop\traceLeak\TraceLeak
git pull --ff-only
pytest tests/test_level18_archive_index.py
pytest tests/test_level18_archive_index_report.py
pytest tests/test_write_level18_files_cli.py
ruff check .
pytest
```

### Completion criteria

- [ ] Focused Level 18 tests pass.
- [ ] `ruff check .` passes.
- [ ] Full `pytest` passes.
- [ ] Level 18 outputs stay under `reports/local/`.

## Stop condition

Stop before Level 19 unless Level 18 focused tests, `ruff check .`, and full `pytest` all pass locally.
