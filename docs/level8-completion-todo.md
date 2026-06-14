# Level 8 Completion TODO

Level 8 is approved metadata artifact intake.

It must remain path-only and metadata/report only. It may reference local artifacts already produced under `reports/local/`, but it must not read raw payload contents, mutate source trees, run external projects, collect raw traces, collect private material, or generate evidence claims.

## Level 8 goal

Create a controlled intake layer for approved local metadata/report artifacts produced by prior levels.

The Level 8 flow is:

```text
Level 7 artifact boundary plan
  -> approved artifact intake manifest
  -> path-only artifact intake validator
  -> path-only artifact index
  -> Level 8 intake report
```

## Level 8 non-goals

- No external project build.
- No external project execution.
- No source tree mutation.
- No patch materialization.
- No raw capture collection.
- No payload collection.
- No private material collection.
- No payload reading.
- No claim generation.

## Level 8 done definition

Level 8 is complete when all of the following are true:

- [ ] A versioned approved artifact intake manifest exists.
- [ ] The manifest requires a valid Level 7 artifact boundary plan.
- [ ] The manifest accepts only classes listed by the boundary plan.
- [ ] The manifest rejects unknown artifact classes.
- [ ] The manifest rejects raw or sensitive artifact classes.
- [ ] All artifact paths must be relative and under `reports/local/`.
- [ ] A path-only intake index exists.
- [ ] The index records path, class, role, existence, and size only.
- [ ] The index does not read JSON or Markdown payload contents.
- [ ] A Level 8 intake report exists.
- [ ] A writer CLI exists for Level 8 intake artifacts.
- [ ] Focused Level 8 tests pass.
- [ ] `ruff check .` passes.
- [ ] Full `pytest` passes.

## P114: approved artifact intake manifest

### Purpose

Define an explicit manifest for accepted local metadata/report artifacts.

### Implementation tasks

- [ ] Add a Level 8 manifest helper.
- [ ] Define `traceleak.level8_artifact_intake_manifest.v1`.
- [ ] Require a valid Level 7 artifact boundary plan.
- [ ] Require manifest entries with:
  - [ ] key
  - [ ] artifact class
  - [ ] relative path
  - [ ] role
- [ ] Accept only artifact classes from the Level 7 accepted list.
- [ ] Reject artifact classes from the Level 7 rejected list.
- [ ] Reject unknown artifact classes.
- [ ] Require paths under `reports/local/`.
- [ ] Reject absolute paths.
- [ ] Reject parent traversal.
- [ ] Keep `payload_reading_allowed = false`.
- [ ] Keep `claim_generation_allowed = false`.

### Tests

- [ ] Build default manifest from a valid Level 7 artifact boundary plan.
- [ ] Reject missing boundary plan linkage.
- [ ] Reject rejected artifact class.
- [ ] Reject unknown artifact class.
- [ ] Reject absolute path.
- [ ] Reject parent traversal.
- [ ] Validate JSON writer.

## P115: artifact intake validator

### Purpose

Harden the manifest validator so future code cannot accidentally widen intake beyond the approved path-only boundary.

### Implementation tasks

- [ ] Validate manifest format and phase.
- [ ] Validate unique artifact keys.
- [ ] Validate artifact classes.
- [ ] Validate path constraints.
- [ ] Validate role strings.
- [ ] Validate no payload-read flag can become true.
- [ ] Validate no claim flag can become true.

### Tests

- [ ] Reject duplicate artifact key.
- [ ] Reject empty role.
- [ ] Reject unsafe path.
- [ ] Reject payload reading enabled.
- [ ] Reject claim generation enabled.

## P116: path-only intake index

### Purpose

Build a path-only index over the manifest entries.

### Implementation tasks

- [ ] Add index builder.
- [ ] Read file metadata only.
- [ ] Record existence.
- [ ] Record size bytes.
- [ ] Do not open or parse artifact payload contents.
- [ ] Record `payload_read = false`.
- [ ] Record `claim_generated = false`.

### Tests

- [ ] Index existing local test files.
- [ ] Index missing paths without failing.
- [ ] Confirm payload-read flag is false.
- [ ] Confirm claim flag is false.
- [ ] Validate JSON writer.

## P117: Level 8 intake report

### Purpose

Render a Markdown report from the path-only index.

### Required sections

- [ ] Intake manifest status.
- [ ] Accepted artifact classes.
- [ ] Rejected artifact classes.
- [ ] Present artifacts.
- [ ] Missing artifacts.
- [ ] Safety boundary.
- [ ] Local validation commands.
- [ ] Next-level preconditions.

### Tests

- [ ] Report contains required headings.
- [ ] Report states payload contents were not read.
- [ ] Report states no claim was generated.
- [ ] Report states artifacts remain under `reports/local/`.

## P118: Level 8 writer CLI

### Purpose

Expose Level 8 path-only intake artifact generation.

### Implementation tasks

- [ ] Add neutral writer CLI name.
- [ ] Build default Level 8 manifest from Level 7 boundary plan.
- [ ] Write manifest JSON.
- [ ] Write path-only index JSON.
- [ ] Write Markdown report.
- [ ] Do not open artifact payloads.
- [ ] Do not execute external commands.
- [ ] Do not mutate source trees.
- [ ] Do not generate claims.

### Tests

- [ ] CLI writes manifest.
- [ ] CLI writes index.
- [ ] CLI writes report.
- [ ] CLI rejects unsafe output root.

## P119: docs and handoff update

### Documentation tasks

- [ ] Update `docs/local-validation.md` with Level 8 focused commands.
- [ ] Update `docs/next-session-handoff.md` with Level 8 status.
- [ ] Update `NEXT_TODO.md` with Level 8 checkpoint.
- [ ] Add Level 8 generation command.
- [ ] Add Level 8 validation command group.

## P120: Level 8 validation checkpoint

### Commands

```powershell
cd C:\Users\junny\Desktop\traceLeak\TraceLeak
git pull --ff-only
pytest tests/test_level8_artifact_intake_manifest.py
pytest tests/test_level8_artifact_intake_index.py
pytest tests/test_level8_artifact_intake_report.py
pytest tests/test_write_level8_artifacts_cli.py
ruff check .
pytest
```

### Completion criteria

- [ ] Focused Level 8 tests pass.
- [ ] `ruff check .` passes.
- [ ] Full `pytest` passes.
- [ ] Level 8 output artifacts stay under `reports/local/`.

## Recommended implementation order

1. P114 approved artifact intake manifest.
2. P115 artifact intake validator hardening.
3. P116 path-only intake index.
4. P117 intake report.
5. P118 writer CLI.
6. P119 docs and handoff update.
7. P120 validation checkpoint.

## Stop condition

Stop before any Level 9 work unless Level 8 focused tests, `ruff check .`, and full `pytest` all pass locally.
