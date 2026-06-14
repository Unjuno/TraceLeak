# Level 8 Completion TODO

Level 8 is approved metadata artifact intake.

It remains path-only and metadata/report only. It references local artifacts under `reports/local/` and records file metadata only.

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

## Level 8 done definition

Level 8 is complete when all of the following are true:

- [x] A versioned approved artifact intake manifest exists.
- [x] The manifest requires a valid Level 7 artifact boundary plan.
- [x] The manifest accepts only classes listed by the boundary plan.
- [x] The manifest rejects unknown artifact classes.
- [x] The manifest rejects raw or sensitive artifact classes.
- [x] All artifact paths must be relative and under `reports/local/`.
- [x] A path-only intake index exists.
- [x] The index records path, class, role, existence, and size only.
- [x] The index does not parse JSON or Markdown contents.
- [x] A Level 8 intake report exists.
- [x] A writer CLI exists for Level 8 intake artifacts.
- [ ] Focused Level 8 tests pass.
- [ ] `ruff check .` passes.
- [ ] Full `pytest` passes.

## P114: approved artifact intake manifest

### Status

- [x] Added Level 8 manifest helper.
- [x] Defined `traceleak.level8_artifact_intake_manifest.v1`.
- [x] Required a valid Level 7 artifact boundary plan.
- [x] Required manifest entries with key, artifact class, relative path, and role.
- [x] Accepted only artifact classes from the Level 7 accepted list.
- [x] Rejected artifact classes from the Level 7 rejected list.
- [x] Rejected unknown artifact classes.
- [x] Required paths under `reports/local/`.
- [x] Rejected absolute paths.
- [x] Rejected parent traversal.
- [x] Kept content-reading and claim flags disabled.
- [x] Added focused tests.

## P115: artifact intake validator

### Status

- [x] Validated manifest format and phase.
- [x] Validated unique artifact keys.
- [x] Validated artifact classes.
- [x] Validated path constraints.
- [x] Validated role strings.
- [x] Validated disabled content-reading flag.
- [x] Validated disabled claim flag.
- [x] Added focused tests.

## P116: path-only intake index

### Status

- [x] Added index builder.
- [x] Reads file metadata only.
- [x] Records existence.
- [x] Records size bytes.
- [x] Does not open or parse artifact contents.
- [x] Records content-read flag as false.
- [x] Records claim flag as false.
- [x] Added focused tests.

## P117: Level 8 intake report

### Status

- [x] Added Markdown report renderer.
- [x] Rendered intake manifest status.
- [x] Rendered accepted artifact classes.
- [x] Rendered rejected artifact classes.
- [x] Rendered present artifacts.
- [x] Rendered missing artifacts.
- [x] Rendered safety boundary.
- [x] Rendered local validation commands.
- [x] Added focused tests.

## P118: Level 8 writer CLI

### Status

- [x] Added neutral writer CLI name: `traceleak-write-level8-files`.
- [x] Built default Level 8 manifest from Level 7 boundary plan.
- [x] Wrote manifest JSON.
- [x] Wrote path-only index JSON.
- [x] Wrote Markdown report.
- [x] Did not parse artifact contents.
- [x] Did not run external commands.
- [x] Did not mutate source trees.
- [x] Did not generate claims.
- [x] Added focused tests.

## P119: docs and handoff update

### Status

- [x] Updated `docs/local-validation.md` with Level 8 focused commands.
- [x] Updated `docs/next-session-handoff.md` with Level 8 status.
- [x] Updated `NEXT_TODO.md` with Level 8 checkpoint.
- [x] Added Level 8 generation command.
- [x] Added Level 8 validation command group.

## P120: Level 8 validation checkpoint

### Commands

```powershell
cd C:\Users\junny\Desktop\traceLeak\TraceLeak
git pull --ff-only
pytest tests/test_level8_artifact_intake_manifest.py
pytest tests/test_level8_artifact_intake_index.py
pytest tests/test_level8_artifact_intake_report.py
pytest tests/test_write_level8_files_cli.py
ruff check .
pytest
```

### Completion criteria

- [ ] Focused Level 8 tests pass.
- [ ] `ruff check .` passes.
- [ ] Full `pytest` passes.
- [ ] Level 8 output artifacts stay under `reports/local/`.

## Current stop condition

Stop before any Level 9 work unless Level 8 focused tests, `ruff check .`, and full `pytest` all pass locally.
