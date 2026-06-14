# TraceLeak NEXT TODO

Current checkpoint: latest local validation reported all pass after the shared pytest fixture addition.

This list covers the next work block. The purpose is to reduce duplicated test setup, improve local reproducibility, and prepare a cleaner handoff into the next metadata sample stage.

## Validation baseline

Run from the repository root:

```powershell
cd C:\Users\junny\Desktop\traceLeak\TraceLeak
git pull --ff-only
ruff check .
pytest
```

## P46: migrate duplicated tests to shared fixtures

Goal: reduce repeated setup code in metadata-demo tests.

- [ ] Update `tests/test_openssl_model_sequence_metadata_demo_manifest.py` to use `metadata_demo_artifacts`.
- [ ] Update `tests/test_metadata_demo_token_ranking.py` to use `metadata_demo_artifacts`.
- [ ] Update any safe P28 tests to use `runtime_transition_gate` where it keeps the test clearer.
- [ ] Keep each test readable; do not over-abstract assertions.
- [ ] Run focused tests and full pytest.

## P47: add lightweight chain-output consistency checks

Goal: verify the one-command demo chain writes the expected set of JSON files.

- [ ] Add a helper function that lists expected demo output names.
- [ ] Add a test that checks every expected file exists after the chain CLI runs.
- [ ] Add a test that each generated file has a JSON object root.
- [ ] Keep generated outputs under pytest temporary directories.
- [ ] Do not commit generated local outputs.

## P48: add a compact fixture usage test

Goal: make `tests/conftest.py` usage explicit and stable.

- [ ] Add a simple test file for shared fixtures if safe to add.
- [ ] Confirm `metadata_demo_artifacts` includes the expected keys.
- [ ] Confirm `runtime_transition_gate` has the expected format and phase.
- [ ] Keep this test minimal to avoid duplicated validation logic.

## P49: add metadata sample shape smoke test

Goal: detect accidental schema drift in generated metadata samples.

- [ ] Check top-level sample fields:
  - `format`,
  - `artifact_format`,
  - `run_count`,
  - `records`,
  - `sample_metadata`.
- [ ] Check every record has:
  - `run_id`,
  - `target`,
  - `view`,
  - `sequence`,
  - `token_counts`,
  - `label`.
- [ ] Keep the test independent of exact NN scores.

## P50: add demo summary smoke test

Goal: ensure P24 summary remains stable enough for later docs and local checks.

- [ ] Verify summary format and phase.
- [ ] Verify baseline and NN summary sections exist.
- [ ] Verify public-safe flags stay true.
- [ ] Verify non-demo claim flags stay false.

## P51: add local command doc refresh

Goal: make the next operator command set shorter.

- [ ] Update `docs/local-validation.md` with the new focused test groups.
- [ ] Add a section for shared fixture tests.
- [ ] Add a section for one-command demo chain output checks.
- [ ] Keep wording short and neutral.

## P52: add developer handoff refresh

Goal: keep long-session recovery easy.

- [ ] Update `docs/next-session-handoff.md` with P46-P51 status after implementation.
- [ ] Include exact validation commands.
- [ ] List known deferred items.
- [ ] Keep the handoff concise.

## P53: inspect old TODO for completed items

Goal: reduce confusion caused by older unchecked P31-P40 entries.

- [ ] Either update `TODO.md` in a small safe patch or keep `NEXT_TODO.md` as the active list.
- [ ] If updating `TODO.md` is blocked again, leave it untouched and reference `NEXT_TODO.md` in final handoff.
- [ ] Do not delete `TODO.md`.

## P54: full local validation checkpoint

Goal: end the block cleanly.

- [ ] Run focused tests.
- [ ] Run `ruff check .`.
- [ ] Run full `pytest`.
- [ ] Fix any failures before starting new feature work.

## P55: choose next technical direction

After P46-P54 are all pass, choose one path:

- [ ] Improve local metadata sample authoring.
- [ ] Improve model-sequence report rendering.
- [ ] Improve fixture generation.
- [ ] Improve docs and public demo onboarding.
- [ ] Improve validation helpers.

Recommended default: improve fixture generation and report rendering, because they increase confidence without expanding scope.
