# Trace Schema

TraceLeak represents each execution as a run containing an ordered sequence of trace events.

The schema is intentionally view-aware. A raw trace may contain secret-equivalent values, while a redacted trace must contain only derived, safer features.

## Run Object

```json
{
  "run_id": "run_000001",
  "target": "openssl-rsa-keygen",
  "target_version": "openssl-3.x",
  "view": "redacted",
  "events": [],
  "labels_lab_only": {}
}
```

## Required Run Fields

| Field | Meaning |
|---|---|
| `run_id` | Unique run identifier |
| `target` | Target implementation or experiment |
| `target_version` | Version or build identifier |
| `view` | Trace view: `meta`, `path`, `redacted`, `observable`, `raw`, or `cheat` |
| `events` | Ordered trace events |

## Lab-Only Label Fields

`labels_lab_only` may contain labels used for local supervised evaluation.

These labels must not be treated as model inputs.

Examples:

```json
{
  "labels_lab_only": {
    "prime_index_bucket": 42,
    "candidate_rank": 17
  }
}
```

## Event Object

```json
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
```

## Required Event Fields

| Field | Required | Meaning |
|---|---:|---|
| `step` | yes | Event order within the run |
| `phase` | yes | High-level phase |
| `function` | yes | Source-level function |
| `event_type` | yes | `assign`, `branch`, `loop`, `phase`, `memory`, `timing` |
| `name` | yes | Variable or event name |
| `file` | recommended | Source file |
| `line` | recommended | Source line |
| `value_type` | optional | Type of captured value |
| `value_raw` | raw only | Raw captured value |
| `value_redacted` | redacted only | Derived representation |

## View Rules

### `meta`

May include only high-level metadata such as target version, key size, provider, build flags, and platform.

### `path`

May include functions, branches, loops, phases, and event names. It must not include raw values.

### `redacted`

May include derived representations such as:

- bit length;
- buckets;
- Hamming weight bucket;
- small modular summaries;
- boolean flags;
- loop count bucket.

### `observable`

May include timing, memory, cache/perf, and other externally observable features collected in a controlled local experiment.

### `raw`

May include raw assignment values. This view is lab-only and must not be published.

### `cheat`

May intentionally include labels or secrets as a positive control. This view must never be used for security claims.

## Public Export Rule

Public trace samples must be synthetic, redacted, path-only, or metadata-only.

Raw and cheat traces must not be committed.
