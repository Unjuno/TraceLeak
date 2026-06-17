# TraceLeak Core Modeling Inventory

Current checkpoint: core roadmap reset. This inventory stops the Level index chain and maps existing code to the Deep Program Representation roadmap.

## Scope rule

A file is considered core modeling work only if it advances at least one of the following:

- program event representation
- variable/state sequence representation
- dependency graph representation
- deep model dataset contract
- sequence or graph model training
- attention / attribution / ablation / evidence-chain explanation
- OpenSSL metadata-to-model-sequence integration

Files that only preserve output paths, write reports, or continue Level N checkpointing are not core modeling work unless explicitly requested as maintenance.

## Current architecture summary

TraceLeak already has a usable early pipeline:

```text
Trace/run events
  -> ordered model steps
  -> token counts
  -> majority / nearest-neighbor / sparse-softmax / MLP baselines
  -> token-level attribution and ablation reports
```

This is useful as a smoke-test path, but it is not yet Deep Program Representation. The current model input collapses ordered execution structure into token counts for most evaluators. That loses long-range order, variable identity continuity, explicit data-flow, control-flow, and state-update causality.

Correct interpretation:

- MLP / local NN: baseline and pipeline smoke test.
- Current attribution: token-level explanation over feature weights or ablation drops.
- Current ablation: feature-family sensitivity check, not causal proof.
- Current OpenSSL path: safety contracts and metadata-only/public-safe sample scaffolding.
- Missing core: first-class event schema, variable state sequence schema, dependency graph schema, and Transformer/GNN-ready dataset contract.

## Inventory table

| Area | File(s) | What exists | Reuse for Deep Program Representation | Limitation / gap |
|---|---|---|---|---|
| Ordered model step extraction | `traceleak/model_features.py` | Converts validated TraceLeak runs into ordered model steps with `event_token`, `source_token`, `context_token`, event type, phase, function/name, optional redacted value tokens. Also builds token vocabulary and token counts. | Reuse as the initial adapter from legacy traces to Program Event Schema v1. | Model steps are not rich events: no explicit reads/writes, operation class, dependency tags, control context object, or stable variable identity. Token-count collapse loses order and structure. |
| Baseline dataset parser | `traceleak/model_sequence_baseline.py` | Parses labeled `examples` or `records`, validates sequence fields, converts sequences/counts to `LabeledFeatureVector`, computes majority and nearest-neighbor leave-one-out baselines. | Reuse parsing and baseline evaluation as negative-control and smoke-test layer. | Input contract is token-count centric. It does not express variable state transitions, graph nodes/edges, masks, or model-ready tensors. |
| Local sparse-softmax NN | `traceleak/model_sequence_nn.py` | Deterministic standard-library single-layer softmax model over sparse token counts. Produces leave-one-out accuracy, chance-adjusted DeltaH proxy, and weight-separation token attributions. | Keep as baseline to test whether extracted features contain any signal. | Not a sequence model. No attention, no graph structure, no variable continuity, no long-range dependency modeling. DeltaH is explicitly a proxy, not a leakage proof. |
| Local MLP | `traceleak/model_sequence_mlp.py` | One-hidden-layer tanh-softmax MLP over sparse token counts. Produces token-level attribution via input-hidden-output bridge scores. | Keep as a stronger smoke-test baseline than sparse softmax. | Still count-based and dependency-light. It cannot be treated as program understanding. It does not model data/control-flow or variable-state causality. |
| NN vs baseline comparison | `traceleak/model_sequence_comparison.py` | Compares sparse-softmax NN leave-one-out accuracy with nearest-neighbor baseline and classifies delta as `neural_better`, `baseline_better`, or `similar`. | Reuse as a required sanity check before interpreting any future deep model result. | Comparison is accuracy-centric. It lacks negative controls at the schema/dataset level and cannot validate causal explanations. |
| Boundary metadata | `traceleak/model_sequence_boundary.py` | Separates toy/local validation from actual trace-derived samples; requires public-safe, redacted, source/build metadata for actual trace-derived samples. | Reuse unchanged as safety boundary for future real trace-derived datasets. | Does not define event/state/graph structure. It only classifies evidence scope. |
| Attribution primitive | `traceleak/attribution.py` | Provides `AttributionScore`, ablation drop scoring, deterministic attribution ranking. | Reuse as the common representation for token/event/variable/edge importance. | Current schema is group-level and scalar. Needs extension for token, event, variable, edge, timestep, and graph-node attribution. |
| Model-sequence audit / ablation | `traceleak/model_sequence_audit.py` | Audits label leakage risk, filters label-proxy tokens, performs feature-family ablations: redacted values, source tokens, context tokens, event-type/phase only, top attribution tokens. | Reuse as required validation around future dataset/model outputs. | Current ablations operate on token-count features, not sequence masks, variable masks, edge masks, or counterfactual state updates. |
| MLP / report chain CLIs | `scripts/train_model_sequence_mlp.py`, `scripts/compare_model_sequence_mlp.py`, `scripts/run_mlp_report_chain.py`, `scripts/run_mlp_expected_check.py`, `scripts/model_sequence_ablation_report.py`, related tests | CLI wrappers around local baseline/model/report paths. | Keep only as validation utilities. | Do not extend into another checkpoint/report chain. They are support tooling, not the main research direction. |
| Token ranking export | `traceleak/metadata_demo_token_ranking.py` | Converts NN result attributions into public-safe ranked token rows with metadata-demo confidence. | Reuse as the seed for a generalized attribution export schema. | Token-only. Needs event/variable/edge-level export and explicit mask semantics. |
| Symbolic / metadata evidence chains | `traceleak/symbolic_metadata_demo_chain.py`, `traceleak/openssl_derived_metadata_profile_demo_chain.py`, related report modules | Maintains public-safe evidence chains around metadata-only or derived metadata demos. | Reuse only as provenance/evidence packaging once real modeling artifacts exist. | Mostly chain/report scaffolding. Does not itself learn representations. |
| OpenSSL event map | `traceleak/openssl_event_map.py` | Validates a pre-instrumentation, execution-disallowed, redacted event-map contract with gates and required controls. | Strong candidate input to Program Event Schema v1; event groups can become planned event templates. | Current event types are limited (`phase`, `loop`, `branch`, `counter`). Missing operation, reads/writes, dependency tags, control context, and graph semantics. |
| OpenSSL trace contract | `traceleak/openssl_trace_contract.py` | Validates a future local collector contract. It declares `traceleak.model_sequence.v1`, required record fields, allowed value channels, disallowed raw-secret fields, and required controls. It does not build, run, instrument, or trace OpenSSL. | Reuse as safety contract for future actual trace-derived dataset ingestion. | Output kind remains `model_sequence_token_counts`; this is too weak for deep sequence/graph modeling. |
| OpenSSL metadata-only model sequence sample | `traceleak/openssl_model_sequence_metadata_sample.py` and related manifest/materialization modules | Builds public-safe metadata-only samples with synthetic lab-only labels and token counts. Explicitly blocks payload/source/command/build/execution/raw capture fields and disables model training/runtime use in metadata. | Reuse as public-safe CI/sample scaffolding only. | Not evidence of OpenSSL leakage. It must not be mistaken for real trace-derived training data. |
| Documentation | `docs/concept.md`, `docs/modeling.md`, `docs/trace_schema.md`, `docs/core-roadmap-reset.md` | Describes concept, modeling assumptions, and reset direction. | Use to align schema design and prevent drift. | Some earlier docs may reflect pre-reset or baseline-heavy framing; schema docs must now supersede Level-index framing. |

## MLP baseline position

MLP is a baseline, not the target architecture.

MLP can validly answer:

- whether current token features contain measurable label signal;
- whether the parser -> feature -> training -> report path runs;
- whether a simple nonlinear baseline beats trivial and nearest-neighbor baselines;
- whether token attribution/ablation reports are mechanically connected.

MLP must not be used to claim:

- long-range program dependency understanding;
- control-flow or data-flow reasoning;
- variable-state causality;
- cryptographic leakage proof;
- real OpenSSL behavior unless backed by actual trace-derived, public-safe, controlled validation.

## Attention / attribution / ablation / evidence-chain status

### Attention

No first-class attention model or attention export schema is present. The existing code has token attributions from sparse-softmax weight separation and MLP bridge scores, but these are not Transformer attention weights.

Needed:

- `attention_export_format.v1` for token/event/variable/edge heads;
- distinction between attention weights, attribution scores, and ablation drops;
- mask metadata showing what was visible to the model.

### Attribution

Present but token/group-level only.

Existing reusable pieces:

- `AttributionScore` as a generic score row;
- deterministic ranking;
- evidence tags;
- model outputs containing `group_id`, `group_type`, `score`, `evidence`.

Needed:

- `group_type` expansion: `event_token`, `variable_state`, `dependency_edge`, `operation`, `branch_context`, `observable_output`;
- timestep and source event IDs;
- score provenance: attention, gradient, integrated gradient, permutation importance, ablation, counterfactual mask;
- uncertainty and negative-control status.

### Ablation

Present for token-count feature families.

Existing reusable pieces:

- redacted-value drop;
- source-token drop;
- context-token drop;
- event-type/phase-only reduction;
- top-attribution token drop;
- label-proxy filtering.

Needed:

- event mask ablation;
- variable mask ablation;
- dependency-edge ablation;
- timestep window ablation;
- control-context ablation;
- counterfactual value-bucket ablation.

### Evidence chain

Present mainly as metadata/demo/report provenance chain. It should be kept, but moved downstream of real modeling artifacts.

Needed evidence-chain units:

```text
raw/public-safe trace contract
  -> normalized ProgramEvent records
  -> VariableStateSequence records
  -> DependencyGraph records
  -> DeepProgramDataset batch
  -> model output
  -> attribution/ablation export
  -> report claim with boundary metadata
```

## Reusable components for next schemas

### Program Event Schema v1 can reuse

From `model_features.py`:

- event ordering: `position`, `step`
- target/view metadata
- event identity: `event_type`, `phase`, `function`, `name`
- source location: `file`, `line`
- tokens: `event_token`, `source_token`, `context_token`
- optional redacted value tokens

From `openssl_event_map.py`:

- event-map safety gates
- allowed redacted event categories
- planned event groups
- forbidden raw value names
- required controls

Must add:

- `event_id`
- `time_step`
- `operation`
- `source_location` object
- `variable_reads`
- `variable_writes`
- `value_class`
- `dependency_tags`
- `control_context`
- `metadata`

### Variable State Sequence Schema v1 can reuse

Current direct reusable implementation is weak. Existing model steps include names/tokens and optional redacted values, but not stable variable-state records.

Must add:

- `sequence_id`
- `time_step`
- `variable_id`
- `scope`
- `state_class`
- `value_observed`
- `value_bucket`
- `source_event_id`
- `depends_on`
- `taint_class`
- `is_secret_derived`
- `metadata`

### Dependency Graph Schema v1 can reuse

Current direct reusable implementation is also weak. Existing code has event/source/context identity but no graph object.

Must add:

- graph nodes: variable, operation, event, branch, memory access, observable output
- graph edges: reads, writes, depends_on, controls, derives, observes
- edge metadata: source event, timestep, dependency kind, confidence, public-safe status
- graph masks for model input

### Deep Model Dataset Contract can reuse

Existing token-count records provide a compatibility path:

```text
legacy token_counts -> event_tokens compatibility view
```

But the primary dataset should become:

```text
{
  "event_tokens": [...],
  "variable_state_tokens": [...],
  "graph_nodes": [...],
  "graph_edges": [...],
  "labels": {...},
  "masks": {...},
  "metadata": {...}
}
```

Required model families:

- sequence model: Transformer or temporal encoder over events and variable-state tokens;
- graph model: GNN/graph Transformer over dependency graph;
- hybrid model: sequence encoder + graph encoder + metadata embeddings;
- explanation layer: attention, attribution, ablation, evidence chain.

## Missing items that should block further modeling claims

The project should not make stronger claims until these exist:

1. `traceleak/program_event_schema.py`
2. `tests/test_program_event_schema.py`
3. `docs/program-event-schema-v1.md`
4. `traceleak/variable_state_sequence.py`
5. `tests/test_variable_state_sequence.py`
6. `docs/variable-state-sequence-v1.md`
7. `traceleak/dependency_graph_schema.py`
8. `tests/test_dependency_graph_schema.py`
9. `docs/dependency-graph-schema-v1.md`
10. `traceleak/deep_program_dataset.py`
11. `tests/test_deep_program_dataset.py`
12. `docs/deep-program-dataset-contract.md`
13. generalized attention/attribution export schema
14. schema-level ablation masks and negative controls

## Immediate next action

Do not create `Level 27 index`.

Next implementation target:

```text
Program Event Schema v1
```

Minimum acceptable implementation:

- dataclass or typed validation helpers for normalized program events;
- strict validation of event IDs, time steps, operation, source location, reads/writes, dependency tags, control context, and metadata;
- conversion helper from legacy `model_features.py` model steps to Program Event records where possible;
- tests covering valid event, missing fields, bad types, deterministic ordering, and legacy conversion;
- documentation explaining how events feed sequence/graph/dataset contracts.

## Decision record

- Continue using existing MLP/NN only as baseline and smoke-test infrastructure.
- Stop extending Level-index/report-only chains.
- Shift implementation to schema-first Deep Program Representation.
- Treat OpenSSL integration as review-only/public-safe unless explicitly validated by local user-run commands.
