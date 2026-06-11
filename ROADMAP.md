# TraceLeak Roadmap

This roadmap tracks the public-safe foundation first, then local-only heavy experiments.

## Current Local Checkpoint

Latest known Windows/Python 3.12 local checkpoint:

```text
129 passed
ruff check .: passed
L5 claim validation: passed
```

This confirms the current public-safe lightweight workflow on the local test environment.

## Milestone 0: Public-Safe Foundation

Status: implemented; GitHub Actions result pending.

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
- patch verification validation;
- patch verification to report conversion;
- repeated-run stability checks;
- claim level validation;
- comparison report rendering;
- synthetic examples;
- toy RSA-like examples;
- lightweight runner;
- public Python API;
- CLI entry points;
- contribution and issue templates;
- release checklist;
- documentation index;
- GitHub Actions CI workflow.

Remaining:

- confirm CI run result on GitHub Actions.

## Milestone 1: Synthetic Leakage Target

Status: implemented as a public-safe lightweight target.

Completed:

- synthetic target generator;
- generated synthetic traces;
- config-driven run;
- attribution sample;
- baseline sample;
- end-to-end tests;
- patch verification sample;
- repeated-run stability sample;
- L5 claim sample;
- leak/control comparison sample;
- patch-style negative control documentation;
- negative control comparison sample.

Remaining:

- generated public comparison artifacts are local-only outputs.

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
- target design documentation;
- generated public report sample;
- synthetic-vs-toy comparison sample;
- public report regeneration tests.

Remaining:

- generated comparison/report artifacts are local-only outputs.

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

Status: implemented for public-safe synthetic evidence.

Completed:

- before/after result schema;
- patch verification validator;
- validation CLI;
- Markdown/JSON report renderer;
- report renderer CLI;
- repeated-run stability checks;
- stability evaluation CLI;
- claim level validation;
- L5 claim support;
- synthetic patch verification sample;
- synthetic stability sample;
- synthetic L5 claim sample;
- patch verification docs;
- stability docs;
- claim level docs;
- unit and CLI tests.

Remaining:

- local implementation evidence integration for M3+.

Success criterion:

```text
A source-localized candidate shows reduced measured signal after controlled modification.
```
