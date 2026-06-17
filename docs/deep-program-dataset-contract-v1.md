# Deep Program Dataset Contract v1

Format identifier: `traceleak.deep_program_dataset.v1`

## Purpose

Deep Program Dataset Contract v1 bundles the schema-first program representation layers into one model-ready sample:

```text
ProgramEvent records
VariableStateRecord records
DependencyGraph records
labels
masks
feature_names
metadata
```

This is the first contract intended to serve sequence-only, graph-only, and hybrid model consumers. It is still a representation contract, not a leakage proof.

## Position in the modeling pipeline

```text
Trace/run events or legacy model_sequence steps
  -> ProgramEvent records
  -> VariableStateRecord records
  -> DependencyGraph records
  -> DeepProgramSample
  -> sequence / graph / hybrid model
  -> attention / attribution / ablation / evidence chain
```

## Required sample fields

| Field | Type | Meaning |
|---|---|---|
| `sample_id` | non-empty string | Stable sample identity. |
| `format` | string | Must equal `traceleak.deep_program_dataset.v1`. |
| `program_events` | non-empty list | Program Event Schema v1 records. |
| `variable_state_sequence` | non-empty list | Variable State Sequence v1 records. |
| `dependency_graph` | object | Dependency Graph Schema v1 object. |
| `labels` | object | Lab-only training target metadata. Must not be public model input. |
| `masks` | object | Consumer-mode masks for sequence, graph, and hybrid models. |
| `feature_names` | object | Declared feature groups for event/state/node/edge consumers. |
| `metadata` | object | Dataset provenance and claim boundary metadata. |

## Labels policy

`labels` must include:

```text
training_target
lab_only
public_model_input
```

`lab_only` must be a boolean. `public_model_input=True` is rejected in public-safe mode.

This separation is deliberate. Supervised local experiments need labels, but labels are not public model features. Mixing training labels into feature inputs is label leakage.

## Masks

`masks` must include:

```text
consumer_modes
use_program_events
use_variable_state_sequence
use_dependency_graph
```

Supported consumer modes:

```text
sequence
graph
hybrid
```

Rules:

```text
sequence -> uses program_events and variable_state_sequence
graph    -> uses dependency_graph
hybrid   -> uses program_events, variable_state_sequence, and dependency_graph
```

The implementation validates consistency. For example, `consumer_modes=["hybrid"]` with `use_dependency_graph=False` is invalid.

## Feature names

`feature_names` must include:

```text
program_event_features
variable_state_features
graph_node_features
graph_edge_features
```

Default feature groups are intentionally simple and schema-level. They are not yet tensor IDs, token IDs, positional encodings, graph adjacency tensors, or attention masks. Those are next-layer dataset-builder concerns.

## Component assembler

`deep_program_sample_from_components()` assembles one sample from:

```text
sample_id
program_events
variable_state_sequence
dependency_graph
labels
consumer_modes
feature_names
metadata
```

It fills default feature names, builds masks from consumer modes, and stamps metadata with:

```text
dataset_kind = deep_program_dataset_sample
claim_scope = representation_only_not_leakage_proof
supports_sequence_model
supports_graph_model
supports_hybrid_model
```

## Public-safety rule

`validate_deep_program_sample(..., public_safe=True)` validates the nested ProgramEvent, VariableStateRecord, and DependencyGraph components. It also rejects raw secret-equivalent field names recursively across the full sample.

Forbidden raw fields include private-key and raw-capture style names such as:

```text
p
q
d
private_key
raw_bignum
raw_capture
raw_secret
rng_state
seed
source_text
command_text
build_output
execution_output
value_raw
```

Variable identifiers, event IDs, node IDs, edge IDs, and bucketized values are allowed when public-safe. Raw secret values are not.

## Minimal example shape

```json
{
  "sample_id": "sample_000001",
  "format": "traceleak.deep_program_dataset.v1",
  "program_events": [],
  "variable_state_sequence": [],
  "dependency_graph": {},
  "labels": {
    "training_target": {"class": "metadata_even"},
    "lab_only": true,
    "public_model_input": false
  },
  "masks": {
    "consumer_modes": ["sequence", "graph", "hybrid"],
    "use_program_events": true,
    "use_variable_state_sequence": true,
    "use_dependency_graph": true
  },
  "feature_names": {
    "program_event_features": ["time_step", "event_type", "operation"],
    "variable_state_features": ["time_step", "variable_id", "state_class"],
    "graph_node_features": ["node_type", "label", "time_step"],
    "graph_edge_features": ["edge_type", "source_node_id", "target_node_id"]
  },
  "metadata": {
    "dataset_kind": "deep_program_dataset_sample",
    "claim_scope": "representation_only_not_leakage_proof"
  }
}
```

The example above shows field shape only. A valid sample requires non-empty `program_events`, non-empty `variable_state_sequence`, and a valid Dependency Graph Schema v1 object.

## What this contract does not yet solve

Deep Program Dataset Contract v1 does not yet define:

- tensorization;
- token vocabulary building;
- event positional encoding;
- variable lifetime encoding;
- graph adjacency matrices;
- graph batching;
- train/validation/test splits;
- attention export;
- gradient attribution export;
- event/variable/edge ablation masks beyond schema-level consumer masks.

Those belong to the next modeling layers.

## Next implementation target

After this contract passes local validation, proceed to:

```text
Attention / Attribution Export Format v1
```

Minimum next units:

```text
sample_id
model_id
model_family
attribution_level
entity_id
entity_type
score
rank
method
evidence
metadata
```

The export format must support token, event, variable, node, and edge attributions without confusing Transformer attention weights with causal explanations.
