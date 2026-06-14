# TraceLeak NEXT TODO

Current checkpoint: P93-P95 one-command local report bundle implemented; local validation pending.

This file is the active short-term TODO. `TODO.md` is kept as historical context and should not be deleted.

## Validation baseline

Run from the repository root:

```powershell
cd C:\Users\junny\Desktop\traceLeak\TraceLeak
git pull --ff-only
ruff check .
pytest
```

Focused validation for the current local report bundle path:

```powershell
pytest tests/test_local_report_bundle.py
pytest tests/test_write_local_report_bundle_cli.py
pytest tests/test_local_demo_dashboard.py tests/test_write_local_demo_dashboard_cli.py
pytest tests/test_demo_summary_comparison.py tests/test_compare_demo_summaries_cli.py
```

## Level 5 completion checklist

- [x] Metadata demo report surfaces implemented.
- [x] Symbolic metadata demo report surfaces implemented.
- [x] Metadata/symbolic summary comparison implemented.
- [x] Combined local dashboard implemented.
- [x] One-command local report bundle implemented.
- [ ] Focused bundle tests still need to be run locally.
- [ ] `ruff check .` still needs to be run locally.
- [ ] Full `pytest` still needs to be run locally.

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
- [x] P92: combined dashboard implemented; local validation pending at handoff time.
- [x] P93: added one-command local report bundle helper.
- [x] P94: added local report bundle smoke tests and CLI.
- [ ] P95: local focused tests, `ruff check .`, and full `pytest` still need to be run locally.

## Candidate next block after local all-pass

### P96: OpenSSL-derived metadata ingestion profile

- [ ] Define the minimal accepted metadata fields for OpenSSL-derived local inputs.
- [ ] Add a profile object that states allowed fields, forbidden fields, and label requirements.
- [ ] Keep the profile metadata-only and payload-free.

### P97: ingestion profile validator

- [ ] Add tests for valid metadata-only OpenSSL-derived records.
- [ ] Reject source text, command text, raw payload, and private material fields.
- [ ] Reject unbalanced labels and unstable run identifiers.

### P98: profile-to-adapter bridge

- [ ] Convert valid profile input into the existing derived metadata adapter input.
- [ ] Prove it still reaches model-sequence, baseline, and NN smoke paths.

### P99: validation checkpoint

- [ ] Run focused Level 6 tests.
- [ ] Run `ruff check .`.
- [ ] Run full `pytest`.

Recommended default: after Level 5 all pass, start Level 6 with the ingestion profile before moving closer to OpenSSL-derived inputs.
