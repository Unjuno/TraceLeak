# Level 25 Completion TODO

Level 25 is path-index planning after Level 24.

Current baseline: Level 25 is locally reported all pass. Level 25 remains review-only and path-only.

## Level 25 goal

Create a path-only index for Level 24 output paths.

## Level 25 done definition

- [x] A versioned index exists.
- [x] The index records expected Level 24 output paths.
- [x] The index records status as pending local validation by default.
- [x] The index remains review-only and path-only.
- [x] A Markdown report exists.
- [x] A writer CLI exists for Level 25 outputs.
- [x] Focused Level 25 tests pass.
- [x] `ruff check .` passes.
- [x] Full `pytest` passes.

## P198: index

### Status

- [x] Added Level 25 index helper.
- [x] Defined `traceleak.level25_index.v1`.
- [x] Recorded expected Level 24 output paths.
- [x] Recorded status as pending local validation.
- [x] Kept review-only and path-only flags.
- [x] Added focused tests.

## P199: report

### Status

- [x] Added Markdown report renderer.
- [x] Rendered status.
- [x] Rendered output paths.
- [x] Rendered expected validation commands.
- [x] Added focused tests.

## P200: writer CLI

### Status

- [x] Added writer CLI name: `traceleak-write-level25-files`.
- [x] Built Level 25 index.
- [x] Rendered report.
- [x] Wrote JSON and Markdown under `reports/local/level25_index/`.
- [x] Added focused tests.

## P201: docs and handoff update

### Status

- [x] Updated `docs/local-validation.md` with Level 25 focused commands.
- [x] Updated `docs/next-session-handoff.md` with Level 25 status.
- [x] Updated `NEXT_TODO.md` with Level 25 checkpoint.
- [x] Added Level 25 generation command.
- [x] Added Level 25 validation command group.

## P202: Level 25 validation checkpoint

### Status

- [x] Focused Level 25 tests reported all pass locally.
- [x] `ruff check .` reported pass locally.
- [x] Full `pytest` reported pass locally.
- [x] Level 25 outputs stay under `reports/local/`.

## Stop condition

Level 25 is complete. Start Level 26 only from a review-only TODO and do not widen behavior directly.
