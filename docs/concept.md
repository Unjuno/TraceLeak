# TraceLeak Concept

TraceLeak is a defensive research framework for implementation-level leakage assessment.

It is not a cryptanalytic attack framework. It does not claim to break RSA or recover third-party secrets. Its purpose is to help a researcher answer whether an implementation trace contains secret-dependent signal, where that signal appears in source-level program behavior, and whether the measured signal decreases after a controlled change.

## Core Concept

TraceLeak is not just a classifier over finished outputs. Its core idea is to learn from the movement of a program while it runs.

A TraceLeak model should receive public-safe representations of:

- which source file, function, line, phase, branch, loop, or variable event occurred;
- when it occurred in the execution sequence;
- how often it occurred;
- how a redacted value-derived feature changed;
- which path or phase transitions happened before and after it;
- which observable timing or memory-adjacent features co-occurred with it.

In other words, the learning target is not only:

```text
trace -> label
```

The intended learning problem is closer to:

```text
program variable/control-flow dynamics -> secret-dependent signal estimate -> source-level attribution
```

TraceLeak treats leakage assessment as a public-safe evidence pipeline:

```text
implementation behavior
  -> variable/control-flow trace collection
  -> public-safe trace views
  -> sequence/feature representation
  -> baseline/model measurement
  -> source-level attribution
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
Which variable, branch, loop, phase, or source-level behavior explains the measured signal,
and does the signal decrease after a controlled modification?
```

## Neural Learning Direction

The neural direction is to model traces as structured execution evidence, not as flat black-box samples.

A future TraceLeak NN can use:

- sequence models over ordered trace events;
- attention over source-level event tokens;
- embeddings for `file:function:line:name` identities;
- embeddings for event types such as branch, loop, phase, assign, memory, and timing;
- redacted value-feature buckets, counts, bit-lengths, Hamming-weight buckets, or modular summaries;
- temporal/context windows around candidate events;
- graph or hierarchy structure from file -> function -> phase -> event.

The model output may be a leakage score, class probability, candidate-space reduction estimate, or ranking. But the important TraceLeak output is the attribution back to source-level behavior.

Attention is useful only as one signal. It should be checked against ablation, baselines, negative controls, repeated-run stability, and patch verification before making a strong claim.

## What TraceLeak Measures

TraceLeak measures implementation-level signal in traces. The main public-safe measurement target is candidate-space reduction:

```text
DeltaH = log2(|C|) - log2(|C_k|)
```

TraceLeak may also report accuracy, top-k recall, ablation drop, repeated-run stability, and report-level comparisons.

## What TraceLeak Localizes

TraceLeak attempts to localize measured signal to source-level groups, such as:

- variables;
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
5. future variable-dynamics model training and heavier local experiments.

This means the public repository should contain reproducible examples and report artifacts, but not raw key-generation traces, private keys, memory dumps, or secret-equivalent material.

## Operating Principle

TraceLeak should make it harder to make vague leakage claims.

A useful TraceLeak result should identify:

- the target;
- the trace view;
- the metric;
- the measured score;
- the source-level variable/control-flow attribution;
- the comparison or control condition;
- the stability evidence;
- the claim level;
- the safety boundary.

In short: TraceLeak turns implementation-level leakage research into an evidence chain over program behavior rather than a one-off score over finished outputs.
