# TraceLeak NEXT TODO

Current checkpoint: P76-P79 local artifact ergonomics block implemented; local validation pending.

This file is the active short-term TODO. `TODO.md` is kept as historical context and should not be deleted.

## Validation baseline

Run from the repository root:

```powershell
cd C:\Users\junny\Desktop\traceLeak\TraceLeak
git pull --ff-only
ruff check .
pytest
```

Focused validation for the current local artifact path:

```powershell
pytest tests/test_metadata_demo_artifact_index.py
pytest tests/test_metadata_demo_readme_snippet.py
pytest tests/test_metadata_demo_metrics.py
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
- [ ] P79: local focused tests, `ruff check .`, and full `pytest` still need to be run locally.

## Candidate next block after local all-pass

### P80: improve symbolic metadata authoring helpers

- [ ] Add a small authoring helper for metadata-only symbolic records.
- [ ] Validate label balance before writing output.
- [ ] Keep it independent from runtime paths.

### P81: add local authoring fixture test

- [ ] Generate a tiny metadata input from symbolic record specs.
- [ ] Adapt it through the existing derived metadata adapter.
- [ ] Confirm it remains parser-compatible with model-sequence tooling.

### P82: add docs for authored symbolic metadata

- [ ] Document the minimal fields.
- [ ] Provide a local-only command path.
- [ ] Keep generated files under `reports/local/`.

### P83: validation checkpoint

- [ ] Run focused tests.
- [ ] Run `ruff check .`.
- [ ] Run full `pytest`.

Recommended default: improve symbolic metadata authoring helpers next, because that moves closer to actual user-controlled sample creation while staying metadata-only.
