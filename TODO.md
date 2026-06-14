# TraceLeak TODO

This TODO tracks the current execution plan for TraceLeak as a public research prototype for source-level leakage localization.

Current status: **P30 public metadata-demo path reached; latest local validation reported all pass**.

The next stage should not jump directly into broad OpenSSL work. The correct next step is to harden the public-safe metadata path, add missing focused tests, add fixtures, and make the end-to-end demo reproducible from a clean checkout. Real OpenSSL build/run/trace work remains outside the default workflow until a later reviewed transition step.

## Operating rules

- Work in repository root: `C:\Users\junny\Desktop\traceLeak\TraceLeak`.
- Repository: `Unjuno/TraceLeak`.
- Branch: `main`.
- Do not delete files or use destructive git operations as part of normal work.
- Do not run, build, instrument, or patch real OpenSSL until the explicit transition path is implemented and reviewed.
- Public demo artifacts must remain metadata-only and payload-free unless a later reviewed step explicitly changes that.
- Every completed phase should have:
  - helper module,
  - focused tests,
  - CLI or validator when appropriate,
  - CLI tests when a CLI exists,
  - `pyproject.toml` entry point when applicable,
  - clear notes that public metadata-demo outputs are not real OpenSSL findings.

## Validation command block

Run this from the repository root after each phase:

```powershell
cd C:\Users\junny\Desktop\traceLeak\TraceLeak
git pull --ff-only
ruff check .
pytest
```

Focused validation for the current OpenSSL metadata-demo chain:

```powershell
cd C:\Users\junny\Desktop\traceLeak\TraceLeak
git pull --ff-only
ruff check .
pytest tests/test_openssl_model_sequence_metadata_sample.py tests/test_build_openssl_model_sequence_metadata_sample_cli.py
pytest tests/test_openssl_model_sequence_metadata_sample_model_preflight.py tests/test_build_openssl_model_sequence_metadata_sample_model_preflight_cli.py
pytest tests/test_run_openssl_model_sequence_metadata_sample_demo_cli.py
pytest
```

## Completed phases

- [x] P6: actual execution readiness report + CLI.
- [x] P7: isolated execution plan-only + CLI.
- [x] P8: reviewed materialization request-only + CLI.
- [x] P9: materialization approval gate + CLI.
- [x] P10: materialization output contract + CLI.
- [x] P11: materialization output manifest validator + CLI.
- [x] P12: manifest-to-model-sequence handoff contract + CLI.
- [x] P13: model-sequence ingestion preflight + CLI.
- [x] P14: model-sequence input contract + CLI.
- [x] P15: model-sequence input manifest validator + CLI.
- [x] P16: model-sequence sample contract + CLI.
- [x] P17: sample manifest validator + CLI.
- [x] P18: sample materialization approval gate + CLI.
- [x] P19: sample materialization request contract + CLI.
- [x] P20: sample materialization output contract + CLI.
- [x] P21: sample materialization output manifest validator + CLI.
- [x] P22: metadata-only `traceleak.model_sequence.v1` sample generator + CLI.
- [x] P23: metadata-only sample to baseline/NN parser preflight + CLI.
- [x] P24: metadata-only baseline / NN demo runner + CLI.
- [x] P25: public-demo documentation plan established. README update needs a smaller safer patch if modified again.
- [x] P26: metadata demo manifest helper + validator CLI.
- [x] P27: OpenSSL target selection plan document.
- [x] P28: conservative transition gate helper + validator CLI.
- [x] P29: symbolic OpenSSL-derived metadata adapter + CLI.
- [x] P30: metadata-demo token ranking helper. CLI was deferred after tool-side safety checks blocked the CLI text.

## Next plan: P31-P40

### P31: harden P26 metadata demo manifest tests

Goal: add focused tests for the P26 metadata demo manifest helper and CLI.

- [ ] Add test file:
  - `tests/test_openssl_model_sequence_metadata_demo_manifest.py`
- [ ] Add CLI test file:
  - `tests/test_validate_openssl_model_sequence_metadata_demo_manifest_cli.py`
- [ ] Test valid manifest generation from P24 outputs.
- [ ] Test manifest validation rejects:
  - mismatched `sample_digest`,
  - missing public-safe statement,
  - `real` claim flags set to true,
  - malformed baseline / NN result binding.
- [ ] Keep all tests self-contained; do not import helper functions from other test modules.
- [ ] Run focused pytest and full pytest.

### P32: harden P28 transition gate tests

Goal: verify that P28 is conservative and does not accidentally enable runtime work.

- [ ] Add test file:
  - `tests/test_openssl_runtime_transition_gate.py`
- [ ] Add CLI test file:
  - `tests/test_validate_openssl_runtime_transition_gate_cli.py`
- [ ] Test valid gate generation.
- [ ] Test validator rejects:
  - wrong target decision,
  - missing reviewer / timestamp,
  - runtime action flag set to true,
  - payload access flag set to true,
  - non-symbolic redaction policy.
- [ ] Confirm P28 remains `review_gate_only`.

### P33: harden P29 symbolic metadata adapter tests

Goal: prove the adapter only accepts public-safe symbolic metadata and produces parser-compatible `traceleak.model_sequence.v1` output.

- [ ] Add test file:
  - `tests/test_openssl_derived_metadata_adapter.py`
- [ ] Add CLI test file:
  - `tests/test_adapt_openssl_derived_metadata_cli.py`
- [ ] Test valid symbolic metadata with at least two labels.
- [ ] Test output can be parsed by existing model-sequence parser.
- [ ] Test rejection of forbidden fields:
  - source text,
  - command text,
  - build output,
  - execution output,
  - raw capture,
  - runtime payload,
  - raw value fields.
- [ ] Test rejection of one-label-only records.

### P34: harden P30 metadata-demo token ranking helper

Goal: make P30 useful without adding a blocked CLI.

- [ ] Add test file:
  - `tests/test_metadata_demo_token_ranking.py`
- [ ] Test valid ranking from demo manifest + NN result.
- [ ] Test ranking rejects:
  - missing sample binding,
  - non-numeric scores,
  - public status flags inconsistent with metadata-only demo.
- [ ] Add Python API usage example in test or docs.
- [ ] Keep CLI deferred unless a safe wording passes review later.

### P35: add public metadata demo fixtures

Goal: avoid rebuilding the long P6-P24 chain in every future test and make the demo easier to inspect.

- [ ] Add small fixture directory:
  - `examples/openssl_metadata_demo/`
- [ ] Add metadata-only fixture JSON files:
  - sample manifest shell,
  - output manifest shell,
  - metadata sample,
  - model preflight,
  - demo summary,
  - baseline result,
  - NN result,
  - demo manifest.
- [ ] Ensure fixtures contain no source text, command text, build output, execution output, raw capture, or runtime payload.
- [ ] Add fixture validation test.
- [ ] Keep fixtures deterministic and small.

### P36: add one-command public demo chain runner

Goal: allow a clean checkout to generate the public metadata demo artifacts with one CLI command.

- [ ] Add helper module:
  - `traceleak/openssl_metadata_demo_chain.py`
- [ ] Add CLI:
  - `scripts/run_openssl_metadata_demo_chain.py`
- [ ] The chain should generate:
  - metadata sample,
  - model preflight,
  - demo summary,
  - baseline result,
  - NN result,
  - demo manifest.
- [ ] Inputs should be limited to output directory and optional record count.
- [ ] Default output path:
  - `reports/local/openssl_metadata_demo/`
- [ ] Add CLI tests.
- [ ] Register entry point.

### P37: add compact README patch for public demo

Goal: update README without a large risky rewrite.

- [ ] Add only a small section, not a full README replacement.
- [ ] Section title:
  - `OpenSSL metadata-only public demo`
- [ ] Explain in no more than 8 bullet points:
  - what the demo proves,
  - what it does not prove,
  - how to run the one-command chain,
  - where outputs are written.
- [ ] Link to:
  - `TODO.md`,
  - `docs/openssl-target-selection.md`.
- [ ] Avoid detailed external-report language in README.

### P38: add docs for symbolic metadata schema

Goal: document the P29 adapter input schema so future OpenSSL-derived metadata can be created consistently.

- [ ] Add doc:
  - `docs/openssl-symbolic-metadata-schema.md`
- [ ] Document required fields:
  - `format`,
  - `source_pin_digest`,
  - `target_decision`,
  - `metadata_only`,
  - `payload_free`,
  - `records`,
  - `source_region_token`,
  - `transition_token`,
  - `label`.
- [ ] Document forbidden fields.
- [ ] Include a minimal safe example.
- [ ] State that schema is symbolic and public-safe.

### P39: add local validation bundle command list

Goal: make handoff easier after long sessions.

- [ ] Add doc:
  - `docs/local-validation.md`
- [ ] Include exact PowerShell commands for:
  - full validation,
  - focused metadata demo validation,
  - fixture validation,
  - chain-runner validation.
- [ ] Note that commands must be run from repo root.
- [ ] Note that generated reports go under `reports/local/`.

### P40: prepare next transition checkpoint

Goal: end the next work block with a clean checkpoint before any real OpenSSL-derived local work.

- [ ] Update `TODO.md` again after P31-P39 are complete.
- [ ] Mark completed hardening phases.
- [ ] List remaining blockers before real OpenSSL-derived local metadata work.
- [ ] Create a concise handoff prompt for the next long session.
- [ ] Ensure `ruff check .` and `pytest` are all pass.

## Later roadmap after P40

Only after P31-P40 are all pass:

- [ ] Build the first local symbolic metadata sample for the selected narrow target.
- [ ] Keep the first sample metadata-only and payload-free.
- [ ] Run the public demo chain over that symbolic sample.
- [ ] Compare symbolic-sample ranking against the metadata-demo fixture ranking.
- [ ] Decide whether the next step should be better instrumentation planning or better report rendering.

## Definition of done for next block

The next block is done when:

```powershell
cd C:\Users\junny\Desktop\traceLeak\TraceLeak
git pull --ff-only
ruff check .
pytest
```

passes, and the repository has:

- focused tests for P26, P28, P29, and P30 helper paths;
- public metadata demo fixtures;
- a one-command metadata demo chain runner;
- compact README documentation;
- symbolic metadata schema docs;
- local validation docs.
