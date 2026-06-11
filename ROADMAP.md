# TraceLeak Roadmap

This roadmap tracks the public-safe foundation first, then local-only heavy experiments.

## Current Local Checkpoint

Latest known Windows/Python 3.12 local checkpoint:

```text
86 passed
```

This confirms the current public-safe lightweight workflow on the local test environment.

## Milestone 0: Public-Safe Foundation

Status: nearly complete.

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
- model result validation;
- model result to report conversion;
- synthetic examples;
- toy RSA-like examples;
- lightweight runner;
- public Python API;
- CLI entry points;
- contribution and issue templates;
- release checklist;
- documentation index.

Remaining:

- CI workflow.

## Milestone 1: Synthetic Leakage Target

Status: implemented as a public-safe lightweight target.

Completed:

- synthetic target generator;
- generated synthetic traces;
- config-driven run;
- attribution sample;
- baseline sample;
- end-to-end tests.

Remaining:

- leak/control comparison report;
- patch-style negative control documentation.

Success criterion:

```text
The known synthetic source event is ranked above unrelated events.
```

## Milestone 2: Toy RSA-Like Target

Status: implemented as a public-safe lightweight target.

Completed:

- toy RSA-like generator;
- safe redacted trace output;
- baseline sample;
- attribution sample;
- config template;
- end-to-end tests;
- target design documentation.

Remaining:

- generated public sample report;
- comparison against synthetic target output.

Success criterion:

```text
TraceLeak can distinguish path-level and redacted-value signal from metadata baseline.
```

## Milestone 3: Local OpenSSL RSA Key Generation

Status: not started. This remains intentionally blocked on M1/M2 validation.

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

Status: result ingestion path implemented; local training remains out of default workflow.

Completed:

- model result JSON schema;
- model result validator;
- model result to report converter;
- attribution import path;
- sample model result;
- CLI tests.

Remaining:

- local NN training harness;
- comparison report between model, majority baseline, and nearest-neighbor baseline.

Success criterion:

```text
NN results are compared against metadata, majority, and nearest-neighbor baselines.
```

## Milestone 5: Patch Verification

Status: not started.

Planned:

- before/after report format;
- stability checks;
- patch verification docs;
- claim level L5 support.

Success criterion:

```text
A source-localized candidate shows reduced measured signal after controlled modification.
```
