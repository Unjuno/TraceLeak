# TraceLeak

**Source-Level Neural Leakage Assessment for Cryptographic Implementations**

TraceLeak is a defensive research framework for detecting, measuring, and localizing secret-dependent leakage in cryptographic implementations.

It uses execution traces, variable-assignment traces, memory/timing observations, and neural/statistical models to answer:

- Does the implementation leak?
- How much information does the trace contain?
- Which source-level variables, branches, phases, or memory/timing features explain the leakage?
- Does the suspected leakage decrease after redaction, ablation, or patching?

TraceLeak does **not** claim to break RSA mathematically. Its purpose is controlled implementation-level leakage assessment.

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

## Initial Roadmap

### Milestone 0: Project Foundation

- Define threat model.
- Define trace schema.
- Implement redaction rules.
- Implement DeltaH metric.
- Add synthetic trace examples.

### Milestone 1: Synthetic Leak Target

Create a small controlled target with an intentionally inserted leak.

Expected result:

```text
TraceLeak ranks the intentionally leaked source-level event as the top leakage source.
```

### Milestone 2: Toy RSA Target

Run a simplified RSA-like key generation process with controlled instrumentation.

Expected result:

```text
TraceLeak detects whether loop counts, rejection reasons, or candidate-derived features correlate with secret-related labels.
```

### Milestone 3: OpenSSL RSA Key Generation

Instrument local OpenSSL RSA key generation.

Expected result:

```text
TraceLeak produces stable source-level leakage rankings for toy OpenSSL RSA key generation traces.
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

Planned structure:

```text
traceleak/
  docs/
  traceleak/
  targets/
    openssl/
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
