# TraceLeak NEXT TODO

Current checkpoint: metadata demo Markdown summary reporter added and latest local validation reported all pass.

This list covers the next work block. The purpose is to improve the human-readable demo output, keep the generated Markdown stable, and connect the Markdown summary more tightly to the one-command metadata demo workflow.

## Validation baseline

Run from the repository root:

```powershell
cd C:\Users\junny\Desktop\traceLeak\TraceLeak
git pull --ff-only
ruff check .
pytest
```

Focused validation for the current reporter path:

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

## P56: add Markdown summary golden-shape test

Goal: make the generated Markdown stable without freezing every numeric value.

- [ ] Add a test that checks required headings appear in order.
- [ ] Check required sections:
  - Status,
  - Safety flags,
  - Baseline,
  - Neural model,
  - Manifest binding,
  - Notes.
- [ ] Check the Markdown ends with a newline or stable final notes block.
- [ ] Avoid exact full-file snapshot testing for now.

## P57: render Markdown summary from one-command chain outputs

Goal: ensure the reporter works against files written by the chain helper, not only in-memory fixtures.

- [ ] Use `write_openssl_metadata_demo_chain` in a pytest temp directory.
- [ ] Read `demo-summary.json` and `demo-manifest.json` from disk.
- [ ] Render Markdown.
- [ ] Assert the output includes sample ID and record count.

## P58: add optional ranking file flow to local docs

Goal: document how to include a ranking JSON when one is available.

- [ ] Update `docs/local-validation.md` with a short optional `--ranking` example.
- [ ] Keep generated files under `reports/local/`.
- [ ] Keep wording short and neutral.

## P59: add Markdown summary chain helper

Goal: reduce repeated CLI usage by adding a helper that writes Markdown from already-built demo artifacts.

- [ ] Add helper function to build ranking and Markdown from `metadata_demo_artifacts`-style objects.
- [ ] Suggested file: extend `traceleak/metadata_demo_markdown_summary.py`.
- [ ] Add tests using `metadata_demo_artifacts`.
- [ ] Keep helper pure and deterministic.

## P60: add chain CLI option to also write Markdown

Goal: let the one-command metadata demo chain optionally create `demo-summary.md`.

- [ ] Add CLI argument to `scripts/run_openssl_metadata_demo_chain.py`:
  - `--write-markdown-summary`
- [ ] When enabled, write `demo-summary.md` in the same output directory.
- [ ] Do not change default behavior.
- [ ] Add CLI test for the option.

## P61: add Markdown summary validation helper

Goal: make it easy to verify a generated Markdown summary file is structurally valid.

- [ ] Add a small validator function for required headings.
- [ ] Add a CLI only if necessary; default to helper tests first.
- [ ] Add tests for valid and missing-heading Markdown.

## P62: update handoff docs after Markdown integration

Goal: keep next-session recovery accurate.

- [ ] Update `docs/next-session-handoff.md` after P56-P61.
- [ ] Include exact focused validation commands.
- [ ] Include the local command to generate JSON + Markdown.

## P63: keep NEXT_TODO active

Goal: avoid confusion with older `TODO.md` entries.

- [ ] Leave `TODO.md` untouched unless a small safe update is needed.
- [ ] Use `NEXT_TODO.md` as the active short-term list.
- [ ] Mention active TODO location in final handoff.

## P64: full local validation checkpoint

Goal: end the block cleanly.

- [ ] Run focused tests.
- [ ] Run `ruff check .`.
- [ ] Run full `pytest`.
- [ ] Fix any failures before starting new feature work.

## P65: choose next technical direction

After P56-P64 are all pass, choose one path:

- [ ] Improve Markdown report quality further.
- [ ] Add CSV or table export for summary metrics.
- [ ] Improve local artifact generation ergonomics.
- [ ] Improve model-sequence report rendering.
- [ ] Improve symbolic metadata authoring helpers.

Recommended default: add `--write-markdown-summary` to the one-command chain and keep report quality incremental.
