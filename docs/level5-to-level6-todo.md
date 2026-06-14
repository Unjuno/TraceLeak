# Level 5 to Level 6 TODO

This list tracks the work required to finish the local metadata-only report surface and then move into OpenSSL-derived metadata ingestion hardening.

## Level 5 completion criteria

- [x] Generate metadata demo JSON, Markdown, metrics, and local artifact index.
- [x] Generate authored symbolic metadata demo JSON and Markdown report.
- [x] Compare metadata demo and symbolic demo summaries.
- [x] Build a combined dashboard over local report surfaces.
- [x] Add a one-command local report bundle writer.
- [ ] Run focused local report bundle tests.
- [ ] Run `ruff check .`.
- [ ] Run full `pytest`.

## Level 6 entry criteria

- [ ] Level 5 full validation is all pass.
- [ ] The local report bundle writes all expected files under `reports/local/`.
- [ ] The bundle summary marks `next_level.level` as `6`.
- [ ] No file payload inspection is introduced in dashboard/index helpers.
- [ ] No OpenSSL build, run, source patch, or raw capture step is introduced.

## Level 6 first work block

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

Recommended next step after Level 5 all pass: implement P96 first, because Level 6 should harden the metadata ingress boundary before moving closer to OpenSSL-derived inputs.
