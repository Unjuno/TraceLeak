# Level 19 Completion TODO

Level 19 is summary planning after Level 18.

Current baseline: Level 18 is locally reported all pass. Level 19 remains review-only and path-only.

## Level 19 goal

Create a final summary layer that references the Level 18 archive index and summarizes the local review chain status.

## Level 19 flow

```text
Level 18 archive index
  -> summary
  -> summary report
  -> writer CLI
  -> validation checkpoint
```

## Level 19 done definition

- [x] A versioned summary exists.
- [x] The summary references the Level 18 archive index format.
- [x] The summary records reviewed levels from 13 through 18.
- [x] The summary records final local status as pending validation by default.
- [x] The summary remains review-only and path-only.
- [x] A summary Markdown report exists.
- [x] A writer CLI exists for Level 19 outputs.
- [ ] Focused Level 19 tests pass.
- [ ] `ruff check .` passes.
- [ ] Full `pytest` passes.

## P168: summary

### Status

- [x] Added Level 19 summary helper.
- [x] Defined `traceleak.level19_summary.v1`.
- [x] Required a valid Level 18 archive index.
- [x] Recorded source index format and phase.
- [x] Recorded reviewed levels:
  - [x] level13.
  - [x] level14.
  - [x] level15.
  - [x] level16.
  - [x] level17.
  - [x] level18.
- [x] Recorded summary status as pending local validation.
- [x] Kept review-only and path-only flags.
- [x] Added focused tests.

## P169: summary report

### Status

- [x] Added Markdown report renderer.
- [x] Rendered summary status.
- [x] Rendered source archive index.
- [x] Rendered reviewed levels.
- [x] Rendered review-only boundary.
- [x] Rendered expected validation commands.
- [x] Rendered next-level preconditions.
- [x] Added focused tests.

## P170: Level 19 writer CLI

### Status

- [x] Added writer CLI name: `traceleak-write-level19-files`.
- [x] Built Level 19 summary.
- [x] Rendered summary report.
- [x] Wrote JSON and Markdown under `reports/local/level19_handoff_summary/`.
- [x] Added focused tests.

## P171: docs and handoff update

### Status

- [x] Updated `docs/local-validation.md` with Level 19 focused commands.
- [x] Updated `docs/next-session-handoff.md` with Level 19 status.
- [x] Updated `NEXT_TODO.md` with Level 19 checkpoint.
- [x] Added Level 19 generation command.
- [x] Added Level 19 validation command group.

## P172: Level 19 validation checkpoint

### Commands

```powershell
cd C:\Users\junny\Desktop\traceLeak\TraceLeak
git pull --ff-only
pytest tests/test_level19_handoff_summary.py
pytest tests/test_level19_handoff_summary_report.py
pytest tests/test_write_level19_files_cli.py
ruff check .
pytest
```

### Completion criteria

- [ ] Focused Level 19 tests pass.
- [ ] `ruff check .` passes.
- [ ] Full `pytest` passes.
- [ ] Level 19 outputs stay under `reports/local/`.

## Stop condition

Stop before Level 20 unless Level 19 focused tests, `ruff check .`, and full `pytest` all pass locally.
