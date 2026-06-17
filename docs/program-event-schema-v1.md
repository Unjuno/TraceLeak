# Program Event Schema v1

Format identifier: `traceleak.program_event.v1`

## Purpose

Program Event Schema v1 is the first schema-first step after the core roadmap reset. Its job is to normalize program execution events before they are consumed by sequence models, graph models, or hybrid Deep Program Representation datasets.

This schema replaces the previous habit of collapsing everything directly into token counts. Token counts remain useful for MLP / sparse-softmax smoke tests, but they are not enough to represent variable motion, state transitions, control context, or dependencies.

## Position in the modeling pipeline

```text
Trace/run events or legacy model_sequence steps
  -> ProgramEvent records
  -> VariableStateSequence records
  -> DependencyGraph records
  -> DeepProgramDataset batches
  -> sequence / graph / hybrid model
  -> attention / attribution / ablation / evidence chain
```

## Required fields

| Field | Type | Meaning |
|---|---|---|
| `event_id` | non-empty string | Stable event identity within a run or sample. |
| `time_step` | non-negative integer | Program-order timestep. Sorting uses `(time_step, event_id)`. |
| `event_type` | enum string | Coarse event family, for example `branch`, `loop`, `memory`, `metadata`, `phase`. |
| `operation` | enum string | Model-facing operation class, for example `load`, `store`, `branch`, `compare`, `crypto_step`. |
| `function` | non-empty string | Function or logical scope where the event occurs. Use `unknown` only when legacy input lacks the field. |
| `source_location` | object | Public-safe source position metadata. Supports `file`, `line`, `column`, `function`. |
| `variable_reads` | list of non-empty strings | Variables read by the event. Empty list is allowed when unknown. |
| `variable_writes` | list of non-empty strings | Variables written or updated by the event. Empty list is allowed when unknown. |
| `value_class` | enum string | Value visibility class: `none`, `public`, `redacted`, `bucket`, `metadata`, `observable`, `secret_derived`, `unknown`. |
| `dependency_tags` | list of non-empty strings | Public-safe dependency labels such as `data_flow`, `control_flow`, `state_update`. |
| `control_context` | object | Branch/loop/phase context visible to the model. |
| `metadata` | object | Provenance and compatibility metadata. |

## Allowed event types

```text
assign
branch
call
compare
counter
crypto
loop
memory
metadata
observable
phase
return
timing
unknown
```

## Allowed operations

```text
arithmetic
assign
branch
call
compare
counter
crypto_step
load
loop
memory_access
metadata
observe
phase
return
store
timing_observation
unknown
```

## Allowed value classes

```text
bucket
metadata
none
observable
public
redacted
secret_derived
unknown
```

## Public-safety rule

`validate_program_event(..., public_safe=True)` rejects raw secret-equivalent field names recursively. This includes fields such as:

```text
p
q
d
private_key
raw_bignum
prime_candidate
seed
rng_state
value_raw
raw_capture
payload
source_text
command_text
build_output
execution_output
```

This does not forbid public-safe variable identifiers in `variable_reads` or `variable_writes`; it forbids raw value payload fields. The distinction matters: a model may need to know that a public-safe variable identity exists, but it must not receive raw secret material.

## Legacy adapter

`program_event_from_legacy_model_step()` converts existing `model_features.py` model steps into ProgramEvent records. It preserves legacy tokens in `metadata`:

```text
legacy_event_token
legacy_source_token
legacy_context_token
legacy_name
legacy_phase
redacted_value_tokens
```

The adapter deliberately does not invent dependencies. If the legacy step lacks `variable_reads`, `variable_writes`, or `dependency_tags`, the ProgramEvent uses empty lists. This is correct: legacy token-count data cannot recover full data-flow or control-flow causality.

## Example

```json
{
  "event_id": "evt_000001",
  "time_step": 1,
  "event_type": "branch",
  "operation": "branch",
  "function": "synthetic_keygen",
  "source_location": {
    "file": "examples/synthetic/target.c",
    "line": 21
  },
  "variable_reads": ["candidate_bucket", "branch_guard"],
  "variable_writes": ["branch_taken"],
  "value_class": "redacted",
  "dependency_tags": ["control_flow", "secret_derived_path"],
  "control_context": {
    "phase": "synthetic_leak",
    "branch_depth": 1
  },
  "metadata": {
    "target": "synthetic-leak",
    "view": "redacted",
    "public_safe": true
  }
}
```

## What this schema does not yet solve

Program Event Schema v1 is necessary but not sufficient. It does not yet define:

- variable-state lifetime records;
- data-flow / control-flow graph edges;
- tensorization for Transformer or GNN batches;
- attention head export;
- gradient or integrated-gradient attribution;
- event/variable/edge ablation masks.

Those belong to the next schemas.

## Next implementation target

After this schema passes local validation, proceed to:

```text
Variable State Sequence Schema v1
```

Minimum next fields:

```text
sequence_id
time_step
variable_id
scope
state_class
value_observed
value_bucket
source_event_id
depends_on
taint_class
is_secret_derived
metadata
```
