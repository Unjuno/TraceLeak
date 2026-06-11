# TraceLeak Concept

TraceLeak is a defensive research framework for implementation-level leakage assessment.

It is not a cryptanalytic attack framework. It does not claim to break RSA or recover third-party secrets. Its purpose is to help a researcher answer whether an implementation trace contains secret-dependent signal, where that signal appears in source-level behavior, and whether the measured signal decreases after a controlled change.

## Core Concept

TraceLeak treats leakage assessment as a public-safe evidence pipeline:

```text
implementation behavior
  -> trace collection
  -> public-safe trace views
  -> feature extraction
  -> baseline/model measurement
  -> attribution
  -> comparison
  -> patch/stability verification
  -> claim level
```

The central question is not only:

```text
Does it leak?
```

The stronger TraceLeak question is:

```text
What source-level behavior explains the measured signal,
and does the signal decrease after a controlled modification?
```

## What TraceLeak Measures

TraceLeak measures implementation-level signal in traces. The main public-safe measurement target is candidate-space reduction:

```text
DeltaH = log2(|C|) - log2(|C_k|)
```

TraceLeak may also report accuracy, top-k recall, ablation drop, repeated-run stability, and report-level comparisons.

## What TraceLeak Localizes

TraceLeak attempts to localize measured signal to source-level groups, such as:

- branches;
- loops;
- phases;
- functions;
- files;
- redacted value-derived features;
- observable timing or memory features.

The purpose of localization is to support defensive review and patch verification, not to expose secret values.

## Public-Safe Views

TraceLeak separates trace data into views:

| View | Role |
|---|---|
| `meta` | Baseline metadata only |
| `path` | Function, branch, loop, and phase behavior |
| `redacted` | Safe derived value features |
| `observable` | Timing, memory, or cache/perf-adjacent features |
| `raw` | Local-only upper-bound analysis |
| `cheat` | Positive-control tests only |

Public examples and public reports should use public-safe views. Raw or secret-equivalent traces remain local-only.

## Claim Discipline

TraceLeak separates measurement from claim strength. A report should not overstate what the evidence supports.

The intended progression is:

```text
synthetic signal
  -> toy target signal
  -> public-safe model/result ingestion
  -> source-level attribution
  -> leak/control comparison
  -> negative control
  -> repeated-run stability
  -> patch verification
  -> L5 claim validation
```

The current L5 direction requires reduced patch-verification evidence and reduced repeated-run stability evidence. This constrains the language of strong claims to cases where the pipeline has more than a single measurement.

## What TraceLeak Is Not

TraceLeak is not:

- a key-recovery tool;
- a remote exploitation framework;
- a production attack workflow;
- a raw memory/RNG exfiltration tool;
- a mathematical RSA cryptanalysis project;
- a license to publish raw secret-equivalent traces.

## Why the Current Repository Looks the Way It Does

The repository is intentionally staged from safe to sensitive:

1. public-safe schemas, metrics, reports, and tests;
2. synthetic and toy targets;
3. comparison, negative-control, stability, and claim-level discipline;
4. future local-only OpenSSL instrumentation;
5. future local-only model training and heavier experiments.

This means the public repository should contain reproducible examples and report artifacts, but not raw key-generation traces, private keys, memory dumps, or secret-equivalent material.

## Operating Principle

TraceLeak should make it harder to make vague leakage claims.

A useful TraceLeak result should identify:

- the target;
- the trace view;
- the metric;
- the measured score;
- the source-level attribution;
- the comparison or control condition;
- the stability evidence;
- the claim level;
- the safety boundary.

In short: TraceLeak turns implementation-level leakage research into an evidence chain rather than a one-off score.
