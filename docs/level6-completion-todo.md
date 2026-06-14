# Level 6 Completion TODO

Level 6 is the OpenSSL-derived metadata ingestion hardening stage.

This level does not introduce OpenSSL build, OpenSSL run, source patching, raw capture, private material collection, or direct execution-output ingestion. It strengthens the boundary between future OpenSSL-derived metadata and the existing TraceLeak model-sequence / baseline / NN / report pipeline.

## Goal

Make TraceLeak ready to accept OpenSSL-derived metadata records from a controlled, payload-free source and prove that those records can safely reach:

1. ingestion profile validation,
2. derived metadata adapter input,
3. model-sequence sample,
4. baseline result,
5. NN result,
6. local report/bundle surface.

## Non-goals

- No OpenSSL build step.
- No OpenSSL execution step.
- No OpenSSL source patch step.
- No raw trace capture step.
- No source text, command text, build output, execution output, raw payload, private key, secret value, or memory dump ingestion.
- No vulnerability claim from metadata-only demo data.

## Level 6 done definition

Level 6 is complete when all of the following are true:

- [ ] A versioned OpenSSL-derived metadata ingestion profile exists.
- [ ] The profile enumerates allowed fields, required fields, optional fields, derived-only fields, and forbidden fields.
- [ ] The profile has explicit label-balance requirements.
- [ ] The profile has stable run identifier rules.
- [ ] The profile has source-region and transition-token normalization rules.
- [ ] The validator rejects any payload-bearing or source-bearing fields recursively.
- [ ] The validator rejects unstable or duplicate run identifiers.
- [ ] The validator rejects label sets that are too small or unbalanced for local model checks.
- [ ] A profile-to-adapter bridge exists.
- [ ] The bridge emits the existing `traceleak.openssl_derived_metadata_input.v1` shape.
- [ ] The bridge output validates with the existing derived metadata adapter.
- [ ] The bridge output reaches `traceleak.model_sequence.v1`.
- [ ] The model-sequence output reaches baseline evaluation.
- [ ] The model-sequence output reaches NN smoke training.
- [ ] A Level 6 local demo chain exists for profile input.
- [ ] A Level 6 summary JSON exists.
- [ ] A Level 6 Markdown report exists.
- [ ] Level 6 outputs can be included in the local report bundle or a follow-up bundle index.
- [ ] Focused Level 6 tests pass.
- [ ] `ruff check .` passes.
- [ ] Full `pytest` passes.

## P96: ingestion profile schema

Create a profile object that describes the acceptable OpenSSL-derived metadata boundary.

### Implementation tasks

- [ ] Add `traceleak/openssl_derived_metadata_profile.py`.
- [ ] Define `OPENSSL_DERIVED_METADATA_PROFILE_FORMAT`, for example `traceleak.openssl_derived_metadata_profile.v1`.
- [ ] Define `OPENSSL_DERIVED_METADATA_PROFILE_PHASE = "P96"`.
- [ ] Define required top-level fields:
  - [ ] `format`
  - [ ] `phase`
  - [ ] `target_decision`
  - [ ] `metadata_only`
  - [ ] `payload_free`
  - [ ] `public_safe`
  - [ ] `label_name`
  - [ ] `source_pin_digest`
  - [ ] `records`
- [ ] Define required record fields:
  - [ ] `run_id`
  - [ ] `source_region_token`
  - [ ] `transition_token`
  - [ ] `label`
- [ ] Define optional safe record fields:
  - [ ] `function_token`
  - [ ] `module_token`
  - [ ] `operation_family`
  - [ ] `observation_class`
  - [ ] `metadata_tags`
- [ ] Define explicitly forbidden fields, recursively:
  - [ ] `source_text`
  - [ ] `diff_text`
  - [ ] `command_text`
  - [ ] `build_output`
  - [ ] `execution_output`
  - [ ] `raw_capture`
  - [ ] `payload`
  - [ ] `private_key`
  - [ ] `secret`
  - [ ] `secret_value`
  - [ ] `value_raw`
  - [ ] `memory_dump`
  - [ ] `trace_bytes`
  - [ ] `stdout`
  - [ ] `stderr`
- [ ] Define `build_openssl_derived_metadata_profile_input(...)` helper.
- [ ] Define `validate_openssl_derived_metadata_profile_input(...)` helper.
- [ ] Define `write_openssl_derived_metadata_profile_input(...)` helper.

### Tests

- [ ] Add `tests/test_openssl_derived_metadata_profile.py`.
- [ ] Validate a minimal balanced profile input.
- [ ] Validate optional safe fields.
- [ ] Reject missing required top-level fields.
- [ ] Reject missing required record fields.
- [ ] Reject forbidden fields recursively.
- [ ] Reject unsafe boolean flags.

## P97: profile validation hardening

Strengthen the validator so profile inputs are stable enough for baseline and NN checks.

### Implementation tasks

- [ ] Require at least four records.
- [ ] Require at least two labels.
- [ ] Require at least two records per label.
- [ ] Require unique `run_id` values.
- [ ] Require stable run IDs matching a conservative pattern, for example `[A-Za-z0-9_.:-]+`.
- [ ] Reject whitespace-only tokens.
- [ ] Reject path-like or parent-traversal tokens.
- [ ] Reject absolute paths in record fields.
- [ ] Reject nested objects except explicitly safe metadata maps.
- [ ] Normalize tokens to strings but do not infer semantic source text.
- [ ] Enforce `target_decision == "constant_time_helper_misuse_path"` until a broader target registry exists.

### Tests

- [ ] Reject duplicate `run_id`.
- [ ] Reject unstable `run_id`.
- [ ] Reject one-sample label buckets.
- [ ] Reject single-label datasets.
- [ ] Reject path traversal in token fields.
- [ ] Reject absolute path tokens.
- [ ] Reject nested forbidden fields.
- [ ] Reject false `metadata_only`, `payload_free`, or `public_safe` flags.

## P98: profile-to-adapter bridge

Convert a validated profile input into the existing adapter input without widening the ingestion surface.

### Implementation tasks

- [ ] Add `adapt_openssl_derived_metadata_profile_to_adapter_input(...)`.
- [ ] Preserve:
  - [ ] `source_pin_digest`
  - [ ] `label_name`
  - [ ] `target_decision`
  - [ ] `records[*].run_id`
  - [ ] `records[*].source_region_token`
  - [ ] `records[*].transition_token`
  - [ ] `records[*].label`
- [ ] Drop or summarize optional safe profile metadata into adapter-safe metadata fields only if existing adapter supports them.
- [ ] Do not include raw source, raw commands, payloads, private material, or execution outputs.
- [ ] Validate bridge output with `validate_openssl_derived_metadata_input(...)`.
- [ ] Validate model-sequence output with existing adapter tests.

### Tests

- [ ] Profile input bridges into `traceleak.openssl_derived_metadata_input.v1`.
- [ ] Bridged input adapts into `traceleak.model_sequence.v1`.
- [ ] Model-sequence output has expected label distribution.
- [ ] Parsed NN vectors have the expected count and labels.
- [ ] Bridge rejects invalid profile input before adapter call.

## P99: Level 6 smoke chain

Create a local smoke chain that starts from the Level 6 profile input and reaches baseline/NN.

### Implementation tasks

- [ ] Add `traceleak/openssl_derived_metadata_profile_demo_chain.py`.
- [ ] Build default balanced profile records.
- [ ] Validate profile input.
- [ ] Bridge profile input to adapter input.
- [ ] Build runtime transition gate.
- [ ] Adapt into model-sequence.
- [ ] Build baseline result.
- [ ] Build NN result.
- [ ] Build compact Level 6 demo summary.
- [ ] Add writer for JSON outputs under `reports/local/openssl_derived_metadata_profile_demo/`.

### Outputs

- [ ] `profile-input.json`
- [ ] `adapter-input.json`
- [ ] `runtime-gate.json`
- [ ] `profile-model-sequence.json`
- [ ] `profile-baseline-result.json`
- [ ] `profile-nn-result.json`
- [ ] `profile-demo-summary.json`

### Tests

- [ ] Chain builds all outputs in memory.
- [ ] Chain writes all expected JSON files.
- [ ] Summary states metadata-only, payload-free, public-safe.
- [ ] Summary states no OpenSSL leakage claim.
- [ ] Summary includes baseline and NN metrics.

## P100: Level 6 Markdown report

Add a human-readable report for the profile demo chain.

### Implementation tasks

- [ ] Add `traceleak/openssl_derived_metadata_profile_report.py`.
- [ ] Render report sections:
  - [ ] profile status
  - [ ] safety boundary
  - [ ] label distribution
  - [ ] baseline metrics
  - [ ] NN metrics
  - [ ] adapter bridge status
  - [ ] next-step guidance
- [ ] Include a clear non-claim note: metadata-only local demo output, not OpenSSL leakage evidence.
- [ ] Add writer helper.

### Tests

- [ ] Markdown report contains required headings.
- [ ] Markdown report includes safety boundary.
- [ ] Markdown report includes baseline and NN metrics.
- [ ] Markdown report rejects malformed summary.

## P101: Level 6 CLI

Expose the profile demo chain through a CLI.

### Implementation tasks

- [ ] Add `scripts/write_openssl_derived_metadata_profile_demo.py` or similarly safe writer-oriented name.
- [ ] Add args:
  - [ ] `--out-dir`
  - [ ] `--epochs`
  - [ ] `--write-report`
- [ ] Register pyproject entry point.
- [ ] Avoid names that imply OpenSSL execution.
- [ ] Keep output under `reports/local/` by documentation.

### Tests

- [ ] CLI writes default profile demo JSON outputs.
- [ ] CLI writes Markdown report when requested.
- [ ] CLI rejects invalid epochs.

## P102: Level 6 bundle integration

Integrate Level 6 profile demo outputs into the existing local report surface.

### Implementation tasks

- [ ] Extend local dashboard expected files with Level 6 profile demo outputs, or add a second dashboard for Level 6.
- [ ] Include `profile-demo-summary.json` and Markdown report in dashboard entries.
- [ ] Extend local report bundle summary with an optional Level 6 readiness marker.
- [ ] Keep dashboard path-only; do not inspect JSON payloads.

### Tests

- [ ] Dashboard includes Level 6 entries when outputs exist.
- [ ] Dashboard marks Level 6 entries missing when outputs do not exist.
- [ ] Bundle summary remains valid.

## P103: local docs and handoff update

Document how Level 6 should be run locally.

### Documentation tasks

- [ ] Update `docs/local-validation.md` with Level 6 focused commands.
- [ ] Update `docs/next-session-handoff.md` with Level 6 checkpoint.
- [ ] Update `NEXT_TODO.md` with P96-P103 status.
- [ ] Add one local generation command for profile demo.
- [ ] Add one full validation block.

## P104: Level 6 validation checkpoint

Run and record local validation.

### Validation commands

```powershell
cd C:\Users\junny\Desktop\traceLeak\TraceLeak
git pull --ff-only
pytest tests/test_openssl_derived_metadata_profile.py
pytest tests/test_openssl_derived_metadata_profile_demo_chain.py
pytest tests/test_openssl_derived_metadata_profile_report.py
pytest tests/test_write_openssl_derived_metadata_profile_demo_cli.py
ruff check .
pytest
```

### Completion criteria

- [ ] Focused Level 6 tests pass.
- [ ] `ruff check .` passes.
- [ ] Full `pytest` passes.
- [ ] Local generation command writes Level 6 profile demo outputs.

## P105: Level 7 readiness review

Do not enter Level 7 automatically. First create a review note stating exactly what Level 6 enables and what it still forbids.

### Review tasks

- [ ] Summarize accepted metadata shape.
- [ ] Summarize forbidden input categories.
- [ ] Summarize adapter bridge behavior.
- [ ] Summarize model-sequence/baseline/NN proof.
- [ ] State that OpenSSL build/run/source patch/raw capture are still outside Level 6.
- [ ] Propose the minimal safe next step for Level 7.

## Recommended execution order

1. P96 profile schema.
2. P97 validator hardening.
3. P98 profile-to-adapter bridge.
4. P99 profile demo chain.
5. P100 Markdown report.
6. P101 CLI.
7. P102 dashboard/bundle integration.
8. P103 docs/handoff/TODO update.
9. P104 validation checkpoint.
10. P105 Level 7 readiness review.
