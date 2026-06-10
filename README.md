# TraceLeak

**Source-Level Neural Leakage Assessment for Cryptographic Implementations**

TraceLeak is a defensive research framework for detecting, measuring, and localizing secret-dependent leakage in cryptographic implementations.

It uses execution traces, variable-assignment traces, memory/timing observations, and neural/statistical models to answer:

- Does the implementation leak?
- How much information does the trace contain?
- Which source-level variables, branches, phases, or memory/timing features explain the leakage?
- Does the suspected leakage decrease after redaction, ablation, or patching?

TraceLeak does **not** claim to break RSA mathematically. Its purpose is controlled implementation-level leakage assessment.

## Current Status

The repository currently contains the lightweight public-safe foundation:

- trace schema validation;
- trace view conversion;
- JSONL IO;
- candidate-space reduction metrics;
- source-level attribution scoring;
- report generation;
- feature extraction;
- baseline evaluation;
- experiment config validation;
- synthetic examples;
- unit tests.

Heavy local work such as neural training, instrumented OpenSSL builds, and large experiments is intentionally not part of the default workflow.

## Quick Start

```bash
git clone https://github.com/Unjuno/TraceLeak.git
cd TraceLeak
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest
```

Windows PowerShell:

```powershell
git clone https://github.com/Unjuno/TraceLeak.git
cd TraceLeak
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
pytest
```

## Lightweight Example Workflow

Validate a synthetic trace:

```bash
python scripts/validate_trace.py --public examples/synthetic/synthetic_trace_sample.jsonl
```

Convert a trace view:

```bash
python scripts/convert_view.py --view path --in examples/synthetic/synthetic_trace_sample.jsonl --out path.jsonl --overwrite
```

Extract features:

```bash
python scripts/extract_features.py --in examples/synthetic/synthetic_trace_sample.jsonl --out features.json
python scripts/extract_features.py --in examples/synthetic/synthetic_trace_sample.jsonl --out features.csv --format csv
```

Evaluate simple baselines:

```bash
python scripts/evaluate_baseline.py --in examples/synthetic/baseline_sample.json
```

Generate an attribution report:

```bash
python scripts/make_report.py --in examples/synthetic/ablation_sample.json --out report.md
python scripts/make_report.py --in examples/synthetic/ablation_sample.json --out report.json --format json
```

Validate an experiment config:

```bash
python scripts/validate_config.py experiments/exp_000_synthetic_leak/config.json
```

Run the lightweight config-driven workflow:

```bash
python scripts/run_experiment.py experiments/exp_000_synthetic_leak/config.json
```

## Initial Target

The initial target is OpenSSL RSA key generation in a local, controlled research environment.

Initial experiments are limited to:

- locally built and instrumented OpenSSL;
- self-generated experimental keys only;
- 256-bit and 512-bit toy RSA experiments;
- source-level trace collection;
- leakage measurement and localization.

The toy key sizes are not security targets. They are used only for controlled experiments and validation of the framework.

## Core Idea

Traditional leakage tests often answer:

```text
Does it leak?
```

TraceLeak aims to also answer:

```text
What leaks?
How much does it leak?
Where in the source does the leakage come from?
Does the leakage decrease after patching?
```

The goal is not only leakage detection, but **leakage localization**.

## Trace Views

TraceLeak separates trace data into multiple views:

| View | Description | Purpose |
|---|---|---|
| `meta` | Version, provider, key size, build config | Baseline |
| `path` | Function, branch, loop, and phase events | Execution-path leakage |
| `redacted` | Derived features such as bit length, buckets, Hamming weight, and modular summaries | Controlled variable leakage |
| `observable` | Timing, cache/perf counters, memory/timing features | Side-channel-adjacent evaluation |
| `raw` | Raw assignment values and internal state | Lab-only upper-bound measurement |
| `cheat` | Intentionally includes labels or secrets | Positive-control tests only |

Security-relevant claims must not be based only on `raw` or `cheat`.

## Leakage Metric

TraceLeak uses candidate-space reduction as a central metric:

```text
DeltaH = log2(|C|) - log2(|C_k|)
```

Where:

- `C` is the original candidate set.
- `C_k` is the candidate set remaining after model ranking.
- `DeltaH` is the candidate-space reduction in bits.

TraceLeak may also report:

- accuracy;
- top-k recall;
- mutual information estimates;
- permutation importance;
- ablation drop;
- source-level leakage ranking;
- cross-snapshot stability checks;
- cross-build stability checks.

## Example Output

```text
Leakage source ranking:

1. crypto/bn/bn_prime.c: candidate_retry_count
   contribution: +5.2 bit DeltaH
   evidence: ablation, permutation importance

2. crypto/rsa/rsa_gen.c: prime_generation_loop
   contribution: +3.1 bit DeltaH
   evidence: path correlation

3. crypto/bn/bn_rand.c: candidate_bitlen_bucket
   contribution: +1.8 bit DeltaH
   evidence: redacted variable signal
```

## Safety Boundary

TraceLeak is for defensive research only.

Allowed:

- local toy experiments;
- self-generated keys;
- source-level leakage assessment;
- defensive regression testing;
- responsible vulnerability research.

Not allowed:

- attacking systems you do not own;
- recovering third-party secrets;
- analyzing third-party private keys;
- exfiltrating memory, RNG state, or private key material;
- targeting production cryptographic services;
- publishing raw secret-equivalent traces.

## Repository Layout

```text
traceleak/
  docs/
  traceleak/
  examples/
    synthetic/
  experiments/
  scripts/
  tests/
```

## License

TraceLeak is released under the Apache License 2.0.

OpenSSL is not bundled unless explicitly added as a third-party dependency or submodule. Any OpenSSL source, fork, or instrumentation patch is governed by its own license terms.

## Status

TraceLeak is experimental research software.

Instrumented cryptographic builds produced for TraceLeak experiments must not be used in production.
