# TraceLeak TODO

This TODO tracks the current execution plan for TraceLeak as a public research prototype for source-level leakage localization.

Current status: **P23 complete**.

TraceLeak is not aiming to accumulate contracts indefinitely. The purpose of the contract and preflight chain is to reach a reproducible path from OpenSSL-derived evidence to `model_sequence` samples, then to baseline / neural evaluation and leakage-candidate ranking.

## Operating rules

- Work in repository root: `C:\Users\junny\Desktop\traceLeak\TraceLeak`.
- Repository: `Unjuno/TraceLeak`.
- Branch: `main`.
- Do not delete files or use destructive git operations as part of normal work.
- Do not run, build, instrument, or patch real OpenSSL until the explicit runtime transition gate is implemented and reviewed.
- Public demo artifacts must remain metadata-only and payload-free unless a later reviewed gate explicitly changes that.
- Every completed phase should have:
  - helper module,
  - focused tests,
  - CLI or validator,
  - CLI tests,
  - `pyproject.toml` entry point when applicable.

## Validation command block

Run this from the repository root after each phase:

```powershell
cd C:\Users\junny\Desktop\traceLeak\TraceLeak
git pull --ff-only
ruff check .
pytest
```

For focused validation of the current OpenSSL metadata sample chain:

```powershell
cd C:\Users\junny\Desktop\traceLeak\TraceLeak
git pull --ff-only
ruff check .
pytest tests/test_openssl_model_sequence_metadata_sample.py tests/test_build_openssl_model_sequence_metadata_sample_cli.py
pytest tests/test_openssl_model_sequence_metadata_sample_model_preflight.py tests/test_build_openssl_model_sequence_metadata_sample_model_preflight_cli.py
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

## Immediate TODO

### P24: metadata-only baseline / NN demo runner

Goal: run the existing model-sequence baseline and neural evaluation over the P22 metadata-only sample, while making it explicit that the result is a public pipeline demo, not an OpenSSL leakage claim.

- [ ] Add helper module, suggested name:
  - `traceleak/openssl_model_sequence_metadata_sample_demo_result.py`
- [ ] Add builder or runner CLI, suggested name:
  - `scripts/run_openssl_model_sequence_metadata_sample_demo.py`
- [ ] Input files:
  - sample contract,
  - sample manifest,
  - approval record,
  - approval gate,
  - request contract,
  - output contract,
  - output manifest,
  - metadata sample,
  - model preflight.
- [ ] Outputs:
  - baseline result JSON,
  - neural result JSON,
  - combined demo summary JSON.
- [ ] Keep safety flags explicit:
  - `metadata_only=True`,
  - `payload_free=True`,
  - `public_safe=True`,
  - `openssl_leakage_claim=False`,
  - `runtime_action_enabled=False`,
  - `payload_access_enabled=False`.
- [ ] Tests:
  - valid chain writes baseline result, NN result, and summary;
  - rejects missing or mismatched preflight;
  - rejects samples with forbidden payload fields;
  - confirms result notes say this is not OpenSSL leakage evidence.
- [ ] Register entry point in `pyproject.toml`.

### P25: README public demo section

Goal: make the public repository understandable without reading the whole conversation history.

- [ ] Add or update README section: `OpenSSL metadata-only demo`.
- [ ] Explain the concept in one paragraph:
  - TraceLeak converts implementation-level evidence into model-sequence samples and uses baseline / neural attribution to rank leakage-relevant variables, transitions, and code regions.
- [ ] Add current status table:
  - completed: P6-P23,
  - next: P24-P27.
- [ ] Add demo command chain for metadata-only flow.
- [ ] Add safety note:
  - current OpenSSL path is metadata-only;
  - no OpenSSL source text, build output, execution output, raw capture, or runtime payload is embedded;
  - demo labels are synthetic lab-only sanity-check labels.

### P26: generated demo artifact validator

Goal: validate the P24 demo output as a stable public artifact.

- [ ] Add helper module:
  - `traceleak/openssl_model_sequence_metadata_demo_manifest.py`
- [ ] Add CLI validator:
  - `scripts/validate_openssl_model_sequence_metadata_demo_manifest.py`
- [ ] Validate:
  - baseline result format,
  - NN result format,
  - summary format,
  - source sample binding,
  - preflight binding,
  - public-safe / metadata-only flags,
  - explicit non-claim status.
- [ ] Tests for valid and invalid manifests.
- [ ] Register entry point.

### P27: OpenSSL target selection plan

Goal: stop treating OpenSSL as one huge target and choose the first narrow analysis target.

Candidate targets:

- [ ] BN modular exponentiation path.
- [ ] RSA private operation path.
- [ ] EC scalar multiplication path.
- [ ] constant-time helper misuse path.
- [ ] parser / decoder path as a non-side-channel comparison target.

Deliverable:

- [ ] `docs/openssl-target-selection.md` or equivalent.
- [ ] Ranking criteria:
  - relevance to leakage localization,
  - feasibility,
  - expected trace shape,
  - risk of false positives,
  - ease of public explanation.

### P28: OpenSSL runtime transition gate

Goal: define the reviewed conditions required before real OpenSSL build / instrumentation / runtime observation is attempted.

- [ ] Add transition gate contract.
- [ ] Require explicit reviewed target selection from P27.
- [ ] Require local-only workspace isolation.
- [ ] Require no source patch application unless separately approved.
- [ ] Require output redaction policy.
- [ ] Require reproducibility metadata.
- [ ] Tests and CLI validator.

### P29: first OpenSSL-derived metadata adapter

Goal: produce OpenSSL-derived metadata samples without embedding source text or raw runtime payload.

- [ ] Define adapter input schema.
- [ ] Define model-sequence output schema.
- [ ] Preserve source location identifiers only as redacted / symbolic tokens.
- [ ] Add parser tests.
- [ ] Add invalid-input tests.

### P30: first leakage-candidate ranking report

Goal: convert baseline / NN / attribution outputs into a report that ranks suspicious variables, transitions, or code regions.

- [ ] Add report helper.
- [ ] Add CLI:
  - `scripts/openssl_model_sequence_candidate_report.py`
- [ ] Inputs:
  - model result,
  - baseline result,
  - sample metadata,
  - target selection metadata.
- [ ] Output:
  - ranked candidate table,
  - evidence type,
  - confidence caveats,
  - no-CVE / no-leakage-claim disclaimer unless proven otherwise.

## Later TODO

### Real OpenSSL analysis path

- [ ] After P28 approval gate, create a local-only experimental path for selected OpenSSL target.
- [ ] Produce minimal redacted trace metadata.
- [ ] Convert redacted metadata into `model_sequence` records.
- [ ] Run baseline and NN evaluation.
- [ ] Produce attribution / ablation report.
- [ ] Manually inspect top candidates.
- [ ] If a candidate is concrete, prepare a responsible disclosure style report.

### Responsible disclosure / bug-report path

Only proceed if real evidence supports a concrete finding.

- [ ] Identify affected OpenSSL version / commit.
- [ ] Identify affected function or code path.
- [ ] Define attacker observation model.
- [ ] Provide minimal reproducibility steps.
- [ ] Separate ML evidence from security impact.
- [ ] Draft private report before any public technical detail is published.

## Definition of done for public demo

The public demo is considered usable when a clean checkout can run:

```powershell
cd C:\Users\junny\Desktop\traceLeak\TraceLeak
ruff check .
pytest
```

and the README explains:

- what TraceLeak does,
- what the OpenSSL metadata-only demo proves,
- what it does not prove,
- how the work proceeds from metadata-only samples toward real OpenSSL leakage localization.
