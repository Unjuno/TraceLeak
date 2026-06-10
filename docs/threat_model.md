# Threat Model

TraceLeak is designed for defensive leakage assessment under controlled local experiments.

It does not model unauthorized access to third-party systems and does not aim to provide operational exploit procedures.

## Observation Levels

| Level | View | Description | Claim Strength |
|---|---|---|---|
| O0 | `meta` | Version, key size, provider, build config | Baseline |
| O1 | `path` | Function, branch, loop, and phase events | Execution-path signal |
| O2 | `redacted` | Derived value features without raw secrets | Controlled variable signal |
| O3 | `observable` | Timing, cache/perf, memory/timing observations | Side-channel-adjacent signal |
| O4 | `raw` | Raw internal values | Lab-only upper bound |
| O5 | `cheat` | Labels or secrets intentionally included | Positive control only |

## Claim Levels

| Level | Claim | Meaning |
|---|---|---|
| L0 | No signal | Trace does not improve over metadata baseline |
| L1 | Raw-only signal | Raw internal values contain information; upper-bound only |
| L2 | Redacted signal | Safe derived features contain measurable signal |
| L3 | Path/observable signal | Execution path or observable features contain signal |
| L4 | Localized signal | Source-level leakage candidate is identified |
| L5 | Patch-verified signal | Modifying the candidate source reduces leakage |

## Non-Goals

TraceLeak does not claim:

- mathematical cryptanalysis of RSA;
- universal breakage of cryptographic algorithms;
- ability to recover secrets from public keys alone;
- real-world exploitability from raw-only lab traces;
- security impact without validation and responsible disclosure.

## Required Controls

Experiments should include:

- metadata-only baseline;
- path-only baseline;
- redacted view evaluation;
- raw upper-bound evaluation only when isolated;
- ablation analysis;
- train/test separation;
- process or snapshot separation;
- patch verification for strong claims.

## Risk Notes

Raw traces may contain secret-equivalent material.

If raw trace access is sufficient to reconstruct private factors, the result should be described as an upper-bound leakage measurement, not as public-key cryptanalysis.
