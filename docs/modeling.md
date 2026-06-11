# Variable and Control-Flow Dynamics Modeling

TraceLeak's modeling direction is not plain output classification. The intended model learns from the movement of a program while it runs.

The model input should represent source-level execution dynamics:

```text
file:function:line:name
  + event_type
  + phase
  + execution order
  + branch/loop/phase transitions
  + redacted value-derived features
  + observable timing or memory-adjacent features
```

The model output may be a leakage score, label probability, candidate-space reduction estimate, or ranking. The important TraceLeak result is the attribution back to source-level behavior.

## Representation

Each trace event can become a model step:

```json
{
  "position": 1,
  "step": 2,
  "event_token": "branch:synthetic_leak:synthetic_keygen:secret_dependent_branch",
  "source_token": "examples/synthetic/target.c:21:synthetic_keygen:secret_dependent_branch",
  "event_type": "branch",
  "phase": "synthetic_leak",
  "function": "synthetic_keygen",
  "name": "secret_dependent_branch",
  "redacted_value_tokens": [
    "value_redacted.branch_taken=true"
  ]
}
```

A full run becomes an ordered sequence of these steps.

## What the NN Should Learn

A future local NN should learn patterns such as:

- whether specific variables or branches correlate with labels;
- whether loop counts or phase transitions carry signal;
- whether redacted value buckets reduce candidate space;
- whether timing or memory-adjacent features co-occur with source-level events;
- whether signal persists across repeated runs;
- whether signal decreases after a controlled patch.

## What the NN Should Not Learn

The public-safe model path must not train on raw secret-equivalent values in public examples.

The model should not receive:

- raw private keys;
- raw RSA factors;
- raw RNG or DRBG state;
- raw prime candidates;
- memory dumps;
- production traces.

Raw local-only views may be useful for upper-bound lab measurements, but they should not be the basis of public claims.

## Attention and Attribution

Attention over source-level tokens may help identify candidate leakage locations, but attention alone is not sufficient evidence.

TraceLeak should validate model attention with:

- ablation;
- baseline comparison;
- negative controls;
- repeated-run stability;
- patch verification;
- claim-level validation.

## Public-Safe Minimal Implementation

The lightweight implementation provides dependency-free helpers that convert a validated run into a sequence representation:

```python
from traceleak.model_features import trace_to_model_sequence

sequence = trace_to_model_sequence(run)
```

This does not train a neural network. It creates the public-safe representation that a local model can consume later.

## Intended Local-Only Future Work

Future local-only work can add:

- sequence model training;
- attention extraction;
- feature-group ablation;
- source-token ranking;
- cross-run stability checks for attention or attribution;
- patch verification using model scores.
