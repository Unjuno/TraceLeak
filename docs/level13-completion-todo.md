# Level 13 Completion TODO

Level 13 is checkpoint closure and handoff manifest planning after Level 12.

Current baseline: Level 12 is locally reported all pass. Level 13 must remain review-only. It may summarize checkpoint state and prepare handoff artifacts, but it must not widen behavior.

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

- [ ] A versioned closure manifest exists.
- [ ] The closure manifest requires a valid Level 12 review checkpoint.
- [ ] The closure manifest records checkpoint status and required preconditions.
- [ ] The closure manifest keeps review-only allowances.
- [ ] A handoff inventory exists.
- [ ] The handoff inventory lists Level 6 through Level 12 artifact families by role.
- [ ] The handoff inventory is path-only.
- [ ] A closure Markdown report exists.
- [ ] A writer CLI exists for Level 13 closure artifacts.
- [ ] Focused Level 13 tests pass.
- [ ] `ruff check .` passes.
- [ ] Full `pytest` passes.

## P137: closure manifest

### Purpose

Define a closure manifest for the Level 12 review checkpoint.

### Implementation tasks

- [ ] Add a Level 13 closure manifest helper.
- [ ] Define `traceleak.level13_closure_manifest.v1`.
- [ ] Require a valid Level 12 review checkpoint.
- [ ] Record source checkpoint format and phase.
- [ ] Record checkpoint status.
- [ ] Record required preconditions.
- [ ] Record closure status:
  - [ ] `ready_for_handoff` when the checkpoint is ready.
  - [ ] `blocked_by_checkpoint` when the checkpoint is blocked.
- [ ] Keep allowances:
  - [ ] closure only true.
  - [ ] direct action false.
  - [ ] content read false.
  - [ ] claim false.

### Tests

- [ ] Build closure manifest from ready checkpoint.
- [ ] Build closure manifest from blocked checkpoint.
- [ ] Reject invalid checkpoint linkage.
- [ ] Reject direct action enabled.
- [ ] Reject content read enabled.
- [ ] Reject claim enabled.
- [ ] Validate JSON writer.

## P138: handoff inventory

### Purpose

Define a path-only handoff inventory for local review artifacts already produced by prior levels.

### Implementation tasks

- [ ] Add handoff inventory helper.
- [ ] Require a valid closure manifest.
- [ ] List artifact families:
  - [ ] Level 6 profile artifacts.
  - [ ] Level 7 planning artifacts.
  - [ ] Level 8 intake artifacts.
  - [ ] Level 9 readiness artifacts.
  - [ ] Level 10 review packet artifacts.
  - [ ] Level 11 next TODO artifacts.
  - [ ] Level 12 checkpoint artifacts.
- [ ] Store path strings only.
- [ ] Require all paths under `reports/local/`.
- [ ] Reject absolute paths.
- [ ] Reject parent traversal.
- [ ] Keep content-read disabled.

### Tests

- [ ] Build default inventory.
- [ ] Reject unsafe path.
- [ ] Reject missing closure linkage.
- [ ] Validate JSON writer.

## P139: closure report

### Purpose

Render a Markdown report for Level 13 closure and handoff status.

### Required sections

- [ ] Closure status.
- [ ] Source checkpoint status.
- [ ] Required preconditions.
- [ ] Handoff inventory summary.
- [ ] Review-only boundary.
- [ ] Local validation commands.
- [ ] Next-level preconditions.

### Tests

- [ ] Report contains required headings.
- [ ] Report states review-only boundary.
- [ ] Report states no content was read.
- [ ] Report states no claim was generated.

## P140: Level 13 writer CLI

### Purpose

Expose Level 13 closure artifact generation.

### Implementation tasks

- [ ] Add neutral writer CLI name.
- [ ] Build closure manifest.
- [ ] Build handoff inventory.
- [ ] Render closure report.
- [ ] Write JSON and Markdown under `reports/local/level13_closure/`.
- [ ] Do not read artifact contents.
- [ ] Do not execute external commands.
- [ ] Do not mutate source trees.
- [ ] Do not generate claims.

### Tests

- [ ] CLI writes closure manifest.
- [ ] CLI writes handoff inventory.
- [ ] CLI writes closure report.
- [ ] CLI rejects bad reviewer or unsafe output path.

## P141: docs and handoff update

### Documentation tasks

- [ ] Update `docs/local-validation.md` with Level 13 focused commands.
- [ ] Update `docs/next-session-handoff.md` with Level 13 status.
- [ ] Update `NEXT_TODO.md` with Level 13 checkpoint.
- [ ] Add Level 13 generation command.
- [ ] Add Level 13 validation command group.

## P142: Level 13 validation checkpoint

### Commands

```powershell
cd C:\Users\junny\Desktop\traceLeak\TraceLeak
git pull --ff-only
pytest tests/test_level13_closure_manifest.py
pytest tests/test_level13_handoff_inventory.py
pytest tests/test_level13_closure_report.py
pytest tests/test_write_level13_files_cli.py
ruff check .
pytest
```

### Completion criteria

- [ ] Focused Level 13 tests pass.
- [ ] `ruff check .` passes.
- [ ] Full `pytest` passes.
- [ ] Level 13 output artifacts stay under `reports/local/`.

## Recommended implementation order

1. P137 closure manifest.
2. P138 handoff inventory.
3. P139 closure report.
4. P140 writer CLI.
5. P141 docs and handoff update.
6. P142 validation checkpoint.

## Stop condition

Stop before Level 14 unless Level 13 focused tests, `ruff check .`, and full `pytest` all pass locally.
