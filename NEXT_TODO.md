# TraceLeak NEXT TODO

Current checkpoint: P90-P92 combined local dashboard implemented; local validation pending.

This file is the active short-term TODO. `TODO.md` is kept as historical context and should not be deleted.

## Validation baseline

Run from the repository root:

```powershell
cd C:\Users\junny\Desktop\traceLeak\TraceLeak
git pull --ff-only
ruff check .
pytest
```

Focused validation for the current local dashboard path:

```powershell
pytest tests/test_local_demo_dashboard.py
pytest tests/test_write_local_demo_dashboard_cli.py
pytest tests/test_demo_summary_comparison.py tests/test_compare_demo_summaries_cli.py
pytest tests/test_symbolic_metadata_demo_chain.py tests/test_run_symbolic_metadata_demo_chain_cli.py
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
- [x] P64: local validation reported all pass.
- [x] P65: selected compact metrics export as the next technical direction.
- [x] P66: added compact demo metrics object.
- [x] P67: added one-row CSV export for demo metrics.
- [x] P68: added chain CLI options for metrics JSON and CSV.
- [x] P69: updated local validation docs.
- [x] P70: updated handoff docs.
- [x] P71-P75: local validation reported all pass.
- [x] P76: added local artifact index helper and Markdown renderer.
- [x] P77: added artifact index CLI outputs.
- [x] P78: added local command snippet generator and CLI output.
- [x] P79: local validation reported all pass.
- [x] P80: added symbolic metadata authoring helper.
- [x] P81: added tests proving authored symbolic input adapts into model-sequence shape.
- [x] P82: added docs and local commands for authored symbolic metadata.
- [x] P83: symbolic authoring block implemented; local validation pending at handoff time.
- [x] P84: connected authored symbolic metadata to adapter, baseline, NN, and JSON summary outputs.
- [x] P85: added authored symbolic Markdown report summary.
- [x] P86: authored symbolic demo chain implemented; local validation pending at handoff time.
- [x] P87: added metadata/symbolic demo summary comparison helper.
- [x] P88: added comparison Markdown renderer and CLI.
- [x] P89: local validation reported all pass.
- [x] P90: added combined local dashboard helper.
- [x] P91: added dashboard Markdown renderer and CLI.
- [ ] P92: local focused tests, `ruff check .`, and full `pytest` still need to be run locally.

## Candidate next block after local all-pass

### P93: add one-command local report bundle runner

- [ ] Run metadata demo generation, symbolic demo generation, comparison, and dashboard generation from one CLI.
- [ ] Keep all outputs under `reports/local/`.
- [ ] Keep it metadata-only and payload-free.

### P94: add bundle smoke tests

- [ ] Verify all expected report surfaces are written.
- [ ] Verify dashboard present count after bundle generation.
- [ ] Verify failure mode for invalid epochs.

### P95: validation checkpoint

- [ ] Run focused tests.
- [ ] Run `ruff check .`.
- [ ] Run full `pytest`.

Recommended default: add a one-command local report bundle next, because it reduces manual steps and prepares a reproducible local demo surface.
