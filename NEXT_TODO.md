# TraceLeak NEXT TODO

Current checkpoint: P84-P86 authored symbolic baseline/NN demo chain implemented; local validation pending.

This file is the active short-term TODO. `TODO.md` is kept as historical context and should not be deleted.

## Validation baseline

Run from the repository root:

```powershell
cd C:\Users\junny\Desktop\traceLeak\TraceLeak
git pull --ff-only
ruff check .
pytest
```

Focused validation for the current authored symbolic demo path:

```powershell
pytest tests/test_symbolic_metadata_demo_chain.py
pytest tests/test_run_symbolic_metadata_demo_chain_cli.py
pytest tests/test_metadata_symbolic_authoring.py
pytest tests/test_build_metadata_symbolic_input_cli.py
pytest tests/test_openssl_derived_metadata_adapter.py tests/test_adapt_openssl_derived_metadata_cli.py
pytest tests/test_openssl_runtime_transition_gate.py tests/test_validate_openssl_runtime_transition_gate_cli.py
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
- [ ] P86: local focused tests, `ruff check .`, and full `pytest` still need to be run locally.

## Candidate next block after local all-pass

### P87: compare metadata-demo and symbolic-demo summaries

- [ ] Add a small comparison helper for two demo summary JSON objects.
- [ ] Compare record count, label distribution, baseline scores, NN scores, and attribution counts.
- [ ] Keep output metadata-only and report-oriented.

### P88: add comparison Markdown report

- [ ] Render a compact Markdown comparison table.
- [ ] Include notes that both sides are metadata-only local demo outputs.
- [ ] Add CLI test coverage.

### P89: validation checkpoint

- [ ] Run focused tests.
- [ ] Run `ruff check .`.
- [ ] Run full `pytest`.

Recommended default: compare the generated metadata demo and authored symbolic demo outputs next, because it helps verify the two local demo surfaces are coherent before moving closer to OpenSSL-derived inputs.
