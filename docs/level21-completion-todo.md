# Level 21 Completion TODO

Level 21 is status-index planning after Level 20.

Current baseline: Level 21 is locally reported all pass. Level 21 remains review-only and path-only.

## Level 21 goal

Create a path-only status index that records Level 20 output paths and local validation state.

## Level 21 done definition

- [x] A versioned status index exists.
- [x] The index records expected Level 20 output paths.
- [x] The index records status as pending local validation by default.
- [x] The index remains review-only and path-only.
- [x] A Markdown report exists.
- [x] A writer CLI exists for Level 21 outputs.
- [x] Focused Level 21 tests pass.
- [x] `ruff check .` passes.
- [x] Full `pytest` passes.

## P178: status index

### Status

- [x] Added Level 21 status-index helper.
- [x] Defined `traceleak.level21_status_index.v1`.
- [x] Recorded expected Level 20 output paths.
- [x] Recorded status as pending local validation.
- [x] Kept review-only and path-only flags.
- [x] Added focused tests.

## P179: status-index report

### Status

- [x] Added Markdown report renderer.
- [x] Rendered status.
- [x] Rendered output paths.
- [x] Rendered review-only boundary.
- [x] Rendered expected validation commands.
- [x] Rendered next-level preconditions.
- [x] Added focused tests.

## P180: Level 21 writer CLI

### Status

- [x] Added writer CLI name: `traceleak-write-level21-files`.
- [x] Built Level 21 status index.
- [x] Rendered status-index report.
- [x] Wrote JSON and Markdown under `reports/local/level21_status_index/`.
- [x] Added focused tests.

## P181: docs and handoff update

### Status

- [x] Updated `docs/local-validation.md` with Level 21 focused commands.
- [x] Updated `docs/next-session-handoff.md` with Level 21 status.
- [x] Updated `NEXT_TODO.md` with Level 21 checkpoint.
- [x] Added Level 21 generation command.
- [x] Added Level 21 validation command group.

## P182: Level 21 validation checkpoint

### Status

- [x] Focused Level 21 tests reported all pass locally.
- [x] `ruff check .` reported pass locally.
- [x] Full `pytest` reported pass locally.
- [x] Level 21 outputs stay under `reports/local/`.

## Stop condition

Level 21 is complete. Start Level 22 only from a review-only TODO and do not widen behavior directly.
