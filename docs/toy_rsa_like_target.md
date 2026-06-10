# Toy RSA-Like Target Design

This document defines the next target after the synthetic example.

The toy RSA-like target is not intended to provide cryptographic security. It exists only to test TraceLeak's measurement and localization workflow on a small key-generation-shaped process.

## Goals

- Use only locally generated toy values.
- Avoid real private keys and production traces.
- Emit public-safe redacted traces by default.
- Compare metadata, path, redacted, and baseline signals.
- Prepare the workflow before any OpenSSL instrumentation work.

## Non-Goals

- No production cryptography.
- No real RSA security claim.
- No third-party key analysis.
- No raw trace publication.
- No default neural training path.

## Proposed Process

```text
seeded toy RNG
  -> candidate generation
  -> oddness check
  -> small divisibility checks
  -> toy primality-like filter
  -> accept/reject loop
  -> redacted trace
```

## Public-Safe Events

| Event | Type | Example redacted values |
|---|---|---|
| `candidate_generated` | phase | bit length bucket |
| `oddness_check` | branch | branch taken |
| `small_factor_check` | loop | divisor bucket, iteration bucket |
| `candidate_rejected` | branch | reason bucket |
| `candidate_accepted` | phase | candidate index bucket |

## Lab-Only Labels

Possible synthetic labels:

- candidate bucket;
- rejection reason bucket;
- accept index bucket;
- toy factor-class bucket.

Labels must remain synthetic and lab-only.

## Trace Views

Default public examples should use:

- `meta`;
- `path`;
- `redacted`.

Raw candidate values must remain local-only.

## Success Criterion

The toy RSA-like target is successful when TraceLeak can show:

```text
redacted/path signal > metadata baseline
```

and source-level attribution identifies the expected toy events above unrelated events.

## Next Implementation Steps

1. Add `examples/toy_rsa_like/target.py`.
2. Generate public-safe redacted JSONL traces.
3. Add toy config under `experiments/`.
4. Add toy baseline sample.
5. Add toy ablation sample.
6. Run the lightweight workflow.
7. Compare toy results against synthetic results.
