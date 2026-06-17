# Variable State Sequence Schema v1

Format identifier: `traceleak.variable_state_sequence.v1`

## Purpose

Variable State Sequence Schema v1 represents variable reads, writes, and coarse state updates as ordered records. It is the second schema-first layer after Program Event Schema v1.

The goal is not to claim full data-flow reconstruction yet. The goal is to stop treating a program as a bag of token counts and start representing variable motion over time.

## Position in the modeling pipeline

```text
ProgramEvent records
  -> VariableStateRecord records
  -> DependencyGraph records
  -> DeepProgramDataset batches
  -> sequence / graph / hybrid model
  -> attention / attribution / ablation / evidence chain
```

## Required fields

| Field | Type | Meaning |
|---|---|---|
| `sequence_id` | non-empty string | Sequence identifier shared by records from one sample/run/view. |
| `time_step` | non-negative integer | Program-order timestep inherited from the source event. |
| `variable_id` | non-empty string | Public-safe variable identity or symbolic variable bucket. |
| `scope` | non-empty string | Function or logical scope where the variable state is observed. |
| `state_class` | enum string | State action: `read`, `write`, `update`, `observe`, `control`, `metadata`, `unknown`. |
| `value_observed` | null / bool / int / float / string | Observed public-safe value. Must be null for redacted or secret-derived records in public-safe mode. |
| `value_bucket` | null or non-empty string | Redacted or bucketized value representation. |
| `source_event_id` | non-empty string | ProgramEvent ID that produced the state record. |
| `depends_on` | list of non-empty strings | Explicit local variable dependencies known to this record. Empty list is allowed. |
| `taint_class` | enum string | `public`, `redacted`, `secret_derived`, `observable`, `metadata`, or `unknown`. |
| `is_secret_derived` | boolean | True only when the state is marked `taint_class=secret_derived`. |
| `metadata` | object | Provenance and model-compatibility metadata. |

## Allowed state classes

```text
control
metadata
observe
read
unknown
update
write
```

## Allowed taint classes

```text
metadata
observable
public
redacted
secret_derived
unknown
```

## Public-safety rule

`validate_variable_state_record(..., public_safe=True)` rejects raw secret-equivalent field names recursively. It also rejects non-null `value_observed` for taint classes other than:

```text
metadata
observable
public
```

Therefore:

```text
secret_derived + value_observed != null  -> invalid
redacted       + value_observed != null  -> invalid
unknown        + value_observed != null  -> invalid
```

Use `value_bucket` for redacted or secret-derived values. Do not place raw big integers, private key material, RNG state, prime candidates, or raw capture payloads in `value_observed` or `metadata`.

## ProgramEvent adapter

`variable_state_records_from_program_events()` derives coarse records from explicit ProgramEvent fields:

```text
ProgramEvent.variable_reads  -> state_class=read
ProgramEvent.variable_writes -> state_class=write
```

For write records, explicit reads from the same event are copied to `depends_on`. This is a coarse local dependency, not a full data-flow proof.

The adapter deliberately refuses to output an empty sequence. If ProgramEvent records have no explicit reads or writes, the correct result is failure, not a fake state sequence.

## Example

```json
{
  "sequence_id": "seq_000001",
  "time_step": 1,
  "variable_id": "branch_taken",
  "scope": "synthetic_keygen",
  "state_class": "write",
  "value_observed": null,
  "value_bucket": "taken",
  "source_event_id": "evt_000001",
  "depends_on": ["candidate_bucket"],
  "taint_class": "secret_derived",
  "is_secret_derived": true,
  "metadata": {
    "target": "synthetic-leak",
    "view": "redacted",
    "public_safe": true
  }
}
```

## Sorting rule

Variable state records are sorted by:

```text
sequence_id
time_step
source_event_id
state_class rank
variable_id
```

State class rank is intentionally not alphabetical. Reads sort before writes so a later dataset builder sees local input states before output/update states at the same timestep.

## What this schema does not yet solve

Variable State Sequence Schema v1 does not yet define:

- graph nodes;
- graph edges;
- full reaching-definition analysis;
- interprocedural aliasing;
- memory object identity;
- event/variable/edge tensorization;
- counterfactual state masking.

Those belong to Dependency Graph Schema v1 and the later Deep Program Dataset Contract.

## Next implementation target

After this schema passes local validation, proceed to:

```text
Dependency Graph Schema v1
```

Minimum next graph units:

```text
nodes:
  variable
  operation
  event
  branch
  memory_access
  observable_output

edges:
  reads
  writes
  depends_on
  controls
  derives
  observes
```
