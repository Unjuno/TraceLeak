# TraceLeak Design v0.1

## 1. Project Definition

TraceLeak is a defensive research framework for detecting, measuring, and localizing secret-dependent leakage in cryptographic implementations.

The project focuses on implementation behavior rather than cryptographic mathematics.

TraceLeak asks:

1. Does an implementation trace contain information about secret-dependent state?
2. How much candidate-space reduction does the trace provide?
3. Which source-level events explain the leakage?
4. Does the measured leakage decrease after ablation, redaction, or patching?

## 2. Initial Scope

### Initial Target

OpenSSL RSA key generation.

### Initial Experiments

- synthetic leakage target;
- toy RSA-like target;
- OpenSSL RSA 256-bit toy key generation;
- OpenSSL RSA 512-bit toy key generation.

### Initial Labels

- prime index bucket;
- candidate-space reduction;
- source-level leakage ranking;
- leakage claim level.

### Out of Scope

- mathematical RSA cryptanalysis;
- third-party key recovery;
- production exploitation;
- remote attacks;
- raw trace publication;
- claims based only on raw internal values.

## 3. Trace Views

TraceLeak separates observations into multiple views.

| View | Description | Claim Strength |
|---|---|---|
| `meta` | Version, provider, key size, build config | Baseline only |
| `path` | Function, branch, loop, phase events | Execution-path signal |
| `redacted` | Value-derived features | Controlled variable signal |
| `observable` | Timing, memory, cache/perf features | Side-channel-adjacent signal |
| `raw` | Raw internal assignment values | Lab-only upper bound |
| `cheat` | Intentionally contains secrets or labels | Positive control only |

The `raw` view is useful for upper-bound analysis, but it is not sufficient for a real security claim.

## 4. Pipeline

```text
target implementation
  ↓
instrumentation
  ↓
trace collection
  ↓
trace normalization
  ↓
trace view generation
  ├─ meta
  ├─ path
  ├─ redacted
  ├─ observable
  └─ raw, lab-only
  ↓
model / statistical test
  ↓
leakage measurement
  ↓
ablation
  ↓
source-level ranking
  ↓
patch verification
```

## 5. Trace Event Schema

Each run is represented as a sequence of events.

```json
{
  "run_id": "run_000001",
  "target": "openssl-rsa-keygen",
  "target_version": "openssl-3.x",
  "view": "redacted",
  "events": [
    {
      "step": 1,
      "phase": "keygen_start",
      "function": "rsa_keygen",
      "file": "crypto/rsa/rsa_gen.c",
      "line": 120,
      "event_type": "phase",
      "name": "keygen_start"
    },
    {
      "step": 2,
      "phase": "prime_generation",
      "function": "BN_generate_prime_ex2",
      "file": "crypto/bn/bn_prime.c",
      "line": 240,
      "event_type": "assign",
      "name": "candidate_retry_count",
      "value_type": "int",
      "value_redacted": {
        "bucket": "16-31",
        "bit_length": 5
      }
    }
  ],
  "labels_lab_only": {
    "prime_index_bucket": 42
  }
}
```

Required event fields:

| Field | Required | Meaning |
|---|---:|---|
| `step` | yes | event order |
| `phase` | yes | high-level phase |
| `function` | yes | source function |
| `event_type` | yes | assign, branch, loop, phase, memory, timing |
| `name` | yes | variable or event name |
| `file` | recommended | source file |
| `line` | recommended | source line |
| `value_raw` | raw only | raw value |
| `value_redacted` | redacted only | safe derived representation |

## 6. Metrics

The central metric is candidate-space reduction:

```text
DeltaH = log2(|C|) - log2(|C_k|)
```

Where:

- `C` is the original candidate set.
- `C_k` is the candidate set remaining after ranking.
- `DeltaH` is measured in bits.

Additional metrics:

- accuracy;
- top-k recall;
- mutual information estimate;
- permutation importance;
- ablation drop;
- cross-snapshot stability;
- cross-build stability.

## 7. Attribution

TraceLeak must not stop at detection.

For each source-level feature group `j`, TraceLeak computes:

```text
s_j = DeltaH(X) - DeltaH(X_without_j)
```

Where:

- `X` is the full input trace view.
- `X_without_j` is the input with feature group `j` removed.
- `s_j` is the leakage contribution score.

Feature groups may be:

- variable;
- branch;
- loop;
- function;
- file;
- phase;
- memory feature;
- timing feature.

## 8. Claim Levels

| Level | Claim | Meaning |
|---|---|---|
| L0 | No signal | Trace does not improve over metadata baseline |
| L1 | Raw-only signal | Raw internal values contain information; upper-bound only |
| L2 | Redacted signal | Safe derived features contain measurable signal |
| L3 | Path/observable signal | Execution path or observable features contain signal |
| L4 | Localized signal | Source-level leakage candidate is identified |
| L5 | Patch-verified signal | Modifying the candidate source reduces leakage |

A strong TraceLeak result should reach at least L4.
A security-relevant result should aim for L5.

## 9. Initial Milestones

### Milestone 0: Foundation

- repository structure;
- license and security policy;
- trace schema;
- redaction rules;
- DeltaH metric;
- synthetic trace examples.

### Milestone 1: Synthetic Leak

Create a controlled target with an intentional secret-dependent branch or memory access.

Success criterion:

```text
TraceLeak ranks the intentionally leaked source-level event as the top leakage source.
```

### Milestone 2: Toy RSA

Create a simplified RSA-like generation target.

Success criterion:

```text
TraceLeak detects whether loop counts, rejection reasons, or redacted candidate features correlate with secret-related labels.
```

### Milestone 3: OpenSSL RSA

Instrument locally built OpenSSL RSA key generation.

Success criterion:

```text
TraceLeak produces stable source-level leakage rankings across process and snapshot boundaries.
```

## 10. Project Principle

TraceLeak should answer:

```text
Not only:
  Does it leak?

But:
  What leaks?
  How much does it leak?
  Where does the leakage come from?
  Does it disappear after patching?
```
