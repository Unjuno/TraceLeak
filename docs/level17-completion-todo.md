# Level 17 Completion TODO

Level 17 is release-readiness checklist planning after Level 16.

Current baseline: Level 17 is locally reported all pass. Level 17 remains review-only and path-only.

## Level 17 goal

Create a release-readiness checklist layer that summarizes whether prior local review artifacts are ready for a later release-style handoff.

The Level 17 flow is:

```text
Level 16 review artifacts
  -> release-readiness checklist
  -> release-readiness report
  -> writer CLI
  -> validation checkpoint
```

## Level 17 non-goals

- No external project build.
- No external project execution.
- No source tree mutation.
- No artifact content parsing.
- No command execution.
- No private material collection.
- No claim generation.

## Level 17 done definition

Level 17 is complete when all of the following are true:

- [x] A versioned release-readiness checklist exists.
- [x] The checklist requires a valid Level 16 review artifact.
- [x] The checklist records review disposition.
- [x] The checklist records expected validation commands.
- [x] The checklist records readiness items with pending local validation by default.
- [x] The checklist remains review-only and path-only.
- [x] A release-readiness Markdown report exists.
- [x] A writer CLI exists for Level 17 artifacts.
- [x] Focused Level 17 tests pass.
- [x] `ruff check .` passes.
- [x] Full `pytest` passes.

## P158: release-readiness checklist

### Status

- [x] Added Level 17 release-readiness helper.
- [x] Defined `traceleak.level17_release_readiness.v1`.
- [x] Required a valid Level 16 review artifact.
- [x] Recorded source review format and phase.
- [x] Recorded review disposition.
- [x] Recorded expected validation commands.
- [x] Recorded readiness items:
  - [x] focused tests pending.
  - [x] ruff pending.
  - [x] full pytest pending.
  - [x] docs updated pending.
- [x] Kept flags:
  - [x] review only true.
  - [x] path only true.
  - [x] content read false.
  - [x] command executed false.
  - [x] claim generated false.
- [x] Added focused tests.

## P159: release-readiness report

### Status

- [x] Added Markdown report renderer.
- [x] Rendered readiness status.
- [x] Rendered source review status.
- [x] Rendered readiness items.
- [x] Rendered expected validation commands.
- [x] Rendered review-only boundary.
- [x] Rendered next-level preconditions.
- [x] Added focused tests.

## P160: Level 17 writer CLI

### Status

- [x] Added neutral writer CLI name: `traceleak-write-level17-files`.
- [x] Built Level 17 release-readiness checklist.
- [x] Rendered release-readiness report.
- [x] Wrote JSON and Markdown under `reports/local/level17_release_readiness/`.
- [x] Did not read artifact contents.
- [x] Did not execute validation commands.
- [x] Did not mutate source trees.
- [x] Did not generate claims.
- [x] Added focused tests.

## P161: docs and handoff update

### Status

- [x] Updated `docs/local-validation.md` with Level 17 focused commands.
- [x] Updated `docs/next-session-handoff.md` with Level 17 status.
- [x] Updated `NEXT_TODO.md` with Level 17 checkpoint.
- [x] Added Level 17 generation command.
- [x] Added Level 17 validation command group.

## P162: Level 17 validation checkpoint

### Status

- [x] Focused Level 17 tests reported all pass locally.
- [x] `ruff check .` reported pass locally.
- [x] Full `pytest` reported pass locally.
- [x] Level 17 output artifacts stay under `reports/local/`.

## Stop condition

Level 17 is complete. Start Level 18 only from a review-only TODO and do not widen behavior directly.
