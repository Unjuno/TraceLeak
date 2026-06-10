# TraceLeak Roadmap

This roadmap tracks the public-safe foundation first, then local-only heavy experiments.

## Milestone 0: Public-Safe Foundation

Status: in progress.

Completed:

- README and safety documentation;
- Apache-2.0 license and notices;
- trace schema validation;
- trace view conversion;
- JSONL IO;
- DeltaH, accuracy, and top-k metrics;
- attribution scoring;
- report generation;
- feature extraction;
- baseline evaluation;
- experiment config validation;
- synthetic examples;
- lightweight runner;
- contribution and issue templates.

Remaining:

- CI workflow;
- docs link cleanup;
- versioned release checklist;
- API reference stub.

## Milestone 1: Synthetic Leakage Target

Goal: prove that TraceLeak can localize a controlled source-level signal.

Planned:

- minimal synthetic target source;
- generated synthetic traces;
- config-driven run;
- attribution report;
- patch-style negative control.

Success criterion:

```text
The known synthetic source event is ranked above unrelated events.
```

## Milestone 2: Toy RSA-Like Target

Goal: evaluate a simple RSA-like workflow without involving production cryptographic material.

Planned:

- toy generator;
- safe redacted trace output;
- baseline comparison;
- attribution report;
- config templates.

Success criterion:

```text
TraceLeak can distinguish path-level and redacted-value signal from metadata baseline.
```

## Milestone 3: Local OpenSSL RSA Key Generation

Goal: run local controlled experiments on toy OpenSSL RSA key generation builds.

Planned:

- local-only OpenSSL setup notes;
- instrumentation patch format;
- raw-to-redacted conversion rules;
- local runner config template;
- no raw public traces.

Success criterion:

```text
Public reports contain only safe derived data and clearly state claim level.
```

## Milestone 4: Neural and Statistical Modeling

Goal: compare simple baselines with local neural models.

Planned:

- local NN interface contract;
- model result JSON schema;
- attribution import path;
- report comparison utilities.

Success criterion:

```text
NN results are compared against metadata, majority, and nearest-neighbor baselines.
```

## Milestone 5: Patch Verification

Goal: show whether candidate source changes reduce measured signal.

Planned:

- before/after report format;
- stability checks;
- patch verification docs;
- claim level L5 support.

Success criterion:

```text
A source-localized candidate shows reduced measured signal after controlled modification.
```
