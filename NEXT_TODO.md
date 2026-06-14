# TraceLeak NEXT TODO

Current checkpoint: P56-P64 metadata demo Markdown integration block implemented; local validation pending.

This file is the active short-term TODO. `TODO.md` is kept as historical context and should not be deleted.

## Validation baseline

Run from the repository root:

```powershell
cd C:\Users\junny\Desktop\traceLeak\TraceLeak
git pull --ff-only
ruff check .
pytest
```

Focused validation for the current Markdown path:

```powershell
pytest tests/test_metadata_demo_markdown_summary.py tests/test_metadata_demo_markdown_summary_cli.py
pytest tests/test_openssl_metadata_demo_chain_outputs.py
pytest tests/test_run_openssl_metadata_demo_chain_cli.py
```

## Completed recent block

- [x] P46: migrated P26/P30 tests to shared metadata demo fixtures.
- [x] P47: added lightweight chain-output consistency checks.
- [x] P48: shared fixture path established in `tests/conftest.py`.
- [x] P49: added metadata sample shape smoke checks.
- [x] P50: added demo summary smoke checks.
- [x] P51: refreshed local validation docs.
- [x] P52: refreshed next-session handoff docs.
- [x] P55-B: added metadata demo Markdown summary helper, CLI, tests, entry point, and docs.
- [x] P56: added Markdown required-heading shape validation and tests.
- [x] P57: added test coverage for Markdown rendering from chain-written JSON files.
- [x] P58: updated local validation docs with Markdown and ranking-enabled commands.
- [x] P59: added helper to render Markdown directly from metadata demo artifacts.
- [x] P60: added `--write-markdown-summary` and `--include-ranking` to the metadata demo chain CLI.
- [x] P61: added Markdown summary validation helper and missing-heading test.
- [x] P62: updated next-session handoff docs.
- [x] P63: kept `NEXT_TODO.md` as the active short-term list.
- [ ] P64: local focused tests, `ruff check .`, and full `pytest` still need to be run locally.

## P65: choose next technical direction after local all-pass

After P64 is all pass, choose one path:

- [ ] Improve Markdown report quality further.
- [ ] Add CSV or table export for summary metrics.
- [ ] Improve local artifact generation ergonomics.
- [ ] Improve model-sequence report rendering.
- [ ] Improve symbolic metadata authoring helpers.

Recommended default: add a compact metrics export, because it complements the Markdown report without expanding scope.

## Candidate next block: P66-P75

### P66: add compact demo metrics object

- [ ] Build a small metrics object from summary and manifest JSON.
- [ ] Include record count, label count, baseline scores, NN score, attribution count, and sample digest.
- [ ] Keep it deterministic and JSON-only.

### P67: add CSV export for demo metrics

- [ ] Render the compact metrics object to one-row CSV.
- [ ] Add helper tests.
- [ ] Add CLI tests only after helper tests pass.

### P68: add chain CLI option for metrics CSV

- [ ] Add an opt-in flag to write `demo-metrics.csv`.
- [ ] Do not change default chain behavior.
- [ ] Add CLI test.

### P69: update local validation docs

- [ ] Add metrics CSV validation commands.
- [ ] Add local command for JSON + Markdown + CSV generation.

### P70: update handoff docs

- [ ] Reflect Markdown and CSV state after implementation.
- [ ] Keep commands concise.

### P71-P75: validation checkpoint

- [ ] Run focused tests.
- [ ] Run `ruff check .`.
- [ ] Run full `pytest`.
- [ ] Fix failures before adding new surface area.
