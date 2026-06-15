# Level 13 Completion TODO

Level 13 is checkpoint closure and handoff manifest planning after Level 12.

Current baseline: Level 12 and Level 13 are locally reported all pass. Level 13 remains review-only. It summarizes checkpoint state and prepares handoff artifacts without widening behavior.

## Level 13 goal

Create a closure layer for the Level 12 review checkpoint and prepare the next safe handoff package.

The Level 13 flow is:

```text
Level 12 review checkpoint
  -> closure manifest
  -> handoff inventory
  -> closure report
  -> writer CLI
  -> validation checkpoint
```

## Level 13 non-goals

- No external project build.
- No external project execution.
- No source tree mutation.
- No patch materialization.
- No raw capture collection.
- No payload collection.
- No private material collection.
- No artifact content parsing.
- No claim generation.

## Level 13 done definition

Level 13 is complete when all of the following are true:

- [x] A versioned closure manifest exists.
- [x] The closure manifest requires a valid Level 12 review checkpoint.
- [x] The closure manifest records checkpoint status and required preconditions.
- [x] The closure manifest keeps review-only allowances.
- [x] A handoff inventory exists.
- [x] The handoff inventory lists Level 6 through Level 12 artifact families by role.
- [x] The handoff inventory is path-only.
- [x] A closure Markdown report exists.
- [x] A writer CLI exists for Level 13 closure artifacts.
- [x] Focused Level 13 tests pass.
- [x] `ruff check .` passes.
- [x] Full `pytest` passes.

## P137: closure manifest

### Status

- [x] Added Level 13 closure manifest helper.
- [x] Defined `traceleak.level13_closure_manifest.v1`.
- [x] Required a valid Level 12 review checkpoint.
- [x] Recorded source checkpoint format and phase.
- [x] Recorded checkpoint status.
- [x] Recorded required preconditions.
- [x] Recorded closure status:
  - [x] `ready_for_handoff` when the checkpoint is ready.
  - [x] `blocked_by_checkpoint` when the checkpoint is blocked.
- [x] Kept allowances:
  - [x] closure only true.
  - [x] direct action false.
  - [x] content read false.
  - [x] claim false.
- [x] Added focused tests.

## P138: handoff inventory

### Status

- [x] Added handoff inventory helper.
- [x] Required a valid closure manifest.
- [x] Listed artifact families:
  - [x] Level 6 profile artifacts.
  - [x] Level 7 planning artifacts.
  - [x] Level 8 intake artifacts.
  - [x] Level 9 readiness artifacts.
  - [x] Level 10 review packet artifacts.
  - [x] Level 11 next TODO artifacts.
  - [x] Level 12 checkpoint artifacts.
- [x] Stored path strings only.
- [x] Required all paths under `reports/local/`.
- [x] Rejected absolute paths.
- [x] Rejected parent traversal.
- [x] Kept content-read disabled.
- [x] Added focused tests.

## P139: closure report

### Status

- [x] Added Markdown report renderer.
- [x] Rendered closure status.
- [x] Rendered source checkpoint status.
- [x] Rendered required preconditions.
- [x] Rendered handoff inventory summary.
- [x] Rendered review-only boundary.
- [x] Rendered local validation commands.
- [x] Added focused tests.

## P140: Level 13 writer CLI

### Status

- [x] Added neutral writer CLI name: `traceleak-write-level13-files`.
- [x] Built closure manifest.
- [x] Built handoff inventory.
- [x] Rendered closure report.
- [x] Wrote JSON and Markdown under `reports/local/level13_closure/`.
- [x] Did not read artifact contents.
- [x] Did not execute external commands.
- [x] Did not mutate source trees.
- [x] Did not generate claims.
- [x] Added focused tests.

## P141: docs and handoff update

### Status

- [x] Updated `docs/local-validation.md` with Level 13 focused commands.
- [x] Updated `docs/next-session-handoff.md` with Level 13 status.
- [x] Updated `NEXT_TODO.md` with Level 13 checkpoint.
- [x] Added Level 13 generation command.
- [x] Added Level 13 validation command group.

## P142: Level 13 validation checkpoint

### Status

- [x] Focused Level 13 tests reported all pass locally.
- [x] `ruff check .` reported pass locally.
- [x] Full `pytest` reported pass locally.
- [x] Level 13 output artifacts stay under `reports/local/`.

## Stop condition

Level 13 is complete. Start Level 14 only from a review-only TODO and do not widen behavior directly.
