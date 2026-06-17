# Dependency Graph Schema v1

Format identifier: `traceleak.dependency_graph.v1`

## Purpose

Dependency Graph Schema v1 represents program events, operation nodes, variable nodes, and coarse dependency edges. It is the third schema-first layer after Program Event Schema v1 and Variable State Sequence Schema v1.

The goal is not to claim complete data-flow recovery. The goal is to preserve explicit read/write/control structure so later Transformer/GNN-ready dataset builders can train on graph-shaped program information instead of only token counts.

## Position in the modeling pipeline

```text
ProgramEvent records
  -> VariableStateRecord records
  -> DependencyGraph records
  -> DeepProgramDataset batches
  -> sequence / graph / hybrid model
  -> attention / attribution / ablation / evidence chain
```

## Graph container fields

| Field | Type | Meaning |
|---|---|---|
| `graph_id` | non-empty string | Stable graph identity for one sample/run/view. |
| `format` | string | `traceleak.dependency_graph.v1`. |
| `nodes` | non-empty list | Dependency graph nodes. |
| `edges` | list | Dependency graph edges. Empty list is valid for a node-only graph, but derived graphs normally contain edges. |
| `metadata` | object | Provenance and claim-scope metadata. |

## Node fields

| Field | Type | Meaning |
|---|---|---|
| `node_id` | non-empty string | Stable node identity. |
| `node_type` | enum string | `variable`, `operation`, `event`, `branch`, `memory_access`, or `observable_output`. |
| `label` | non-empty string | Model-facing readable label. |
| `source_event_id` | non-empty string | ProgramEvent ID that introduced or justified the node. |
| `time_step` | non-negative integer | Program-order timestep. |
| `metadata` | object | Public-safe provenance and derivation metadata. |

## Edge fields

| Field | Type | Meaning |
|---|---|---|
| `edge_id` | non-empty string | Stable edge identity. |
| `edge_type` | enum string | `reads`, `writes`, `depends_on`, `controls`, `derives`, or `observes`. |
| `source_node_id` | non-empty string | Source node. Must exist in the graph. |
| `target_node_id` | non-empty string | Target node. Must exist in the graph. |
| `source_event_id` | non-empty string | ProgramEvent ID that introduced or justified the edge. |
| `time_step` | non-negative integer | Program-order timestep. |
| `metadata` | object | Public-safe provenance, confidence, and derivation metadata. |

## Supported node types

```text
event
operation
branch
memory_access
observable_output
variable
```

Operation nodes are specialized into `branch`, `memory_access`, or `observable_output` when the ProgramEvent operation makes that safe and explicit. Otherwise they remain `operation`.

## Supported edge types

```text
controls
reads
writes
depends_on
derives
observes
```

## Derived coarse graph helper

`dependency_graph_from_program_events_and_variable_states()` builds a coarse dependency graph from explicit ProgramEvent and VariableStateRecord fields.

It creates:

```text
ProgramEvent             -> event node
ProgramEvent.operation   -> operation / branch / memory / observable node
VariableStateRecord      -> variable node
ProgramEvent -> operation node       edge_type=controls
variable -> operation node for reads edge_type=reads
operation -> variable node for writes edge_type=writes
depends_on variable -> written variable edge_type=depends_on
```

This helper deliberately marks graph metadata with:

```text
graph_kind = coarse_dependency_graph
claim_scope = representation_only_not_leakage_proof
```

Edges include `metadata.derivation_method` and `metadata.confidence`, for example:

```text
program_event_operation_link
variable_state_record
same_event_variable_state_depends_on
coarse_local_dependency
explicit_record
```

## Public-safety rule

`validate_dependency_graph(..., public_safe=True)` rejects raw secret-equivalent field names recursively. Do not place raw bignums, private key fields, RNG state, prime candidates, raw trace payloads, source text, command text, build output, or execution output in graph metadata.

Variable identifiers are allowed when public-safe. Raw values are not.

## Example

```text
event:evt_000001
  --controls--> branch:evt_000001:branch

variable:synthetic_keygen:candidate_bucket
  --reads--> branch:evt_000001:branch

branch:evt_000001:branch
  --writes--> variable:synthetic_keygen:branch_taken

variable:synthetic_keygen:candidate_bucket
  --depends_on--> variable:synthetic_keygen:branch_taken
```

## What this schema does not yet solve

Dependency Graph Schema v1 does not yet implement:

- reaching-definition analysis;
- alias analysis;
- memory object identity;
- interprocedural data-flow;
- symbolic expression normalization;
- graph batching;
- node/edge feature tensorization;
- graph attention export;
- event/variable/edge counterfactual masking.

Those belong to the Deep Program Dataset Contract and later modeling layers.

## Next implementation target

After this schema passes local validation, proceed to:

```text
Deep Program Dataset Contract v1
```

Minimum next units:

```text
sample_id
format
program_events
variable_state_sequence
dependency_graph
labels
masks
feature_names
metadata
```

The dataset contract should support sequence-only, graph-only, and hybrid model consumers without claiming real OpenSSL leakage unless backed by actual trace-derived validation.
