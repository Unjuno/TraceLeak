# Level 24 Completion TODO

Level 24 is path-index planning after Level 23.

Current baseline: Level 24 is locally reported all pass. Level 24 remains review-only and path-only.

## Level 24 goal

Create a path-only index for Level 23 output paths.

## Level 24 done definition

- [x] A versioned index exists.
- [x] The index records expected Level 23 output paths.
- [x] The index records status as pending local validation by default.
- [x] The index remains review-only and path-only.
- [x] A Markdown report exists.
- [x] A writer CLI exists for Level 24 outputs.
- [x] Focused Level 24 tests pass.
- [x] `ruff check .` passes.
- [x] Full `pytest` passes.

## P193: index

### Status

- [x] Added Level 24 index helper.
- [x] Defined `traceleak.level24_index.v1`.
- [x] Recorded expected Level 23 output paths.
- [x] Recorded status as pending local validation.
- [x] Kept review-only and path-only flags.
- [x] Added focused tests.

## P194: report

### Status

- [x] Added Markdown report renderer.
- [x] Rendered status.
- [x] Rendered output paths.
- [x] Rendered review-only boundary.
- [x] Rendered expected validation commands.
- [x] Added focused tests.

## P195: writer CLI

### Status

- [x] Added writer CLI name: `traceleak-write-level24-files`.
- [x] Built Level 24 index.
- [x] Rendered report.
- [x] Wrote JSON and Markdown under `reports/local/level24_index/`.
- [x] Added focused tests.

## P196: docs and handoff update

### Status

- [x] Updated `docs/next-session-handoff.md` with Level 24 status.
- [x] Updated `NEXT_TODO.md` with Level 24 checkpoint.
- [x] Added Level 24 generation command.
- [x] Added Level 24 validation command group.

## P197: Level 24 validation checkpoint

### Status

- [x] Focused Level 24 tests reported all pass locally.
- [x] `ruff check .` reported pass locally.
- [x] Full `pytest` reported pass locally.
- [x] Level 24 outputs stay under `reports/local/`.

## Stop condition

Level 24 is complete. Start Level 25 only from a review-only TODO and do not widen behavior directly.
