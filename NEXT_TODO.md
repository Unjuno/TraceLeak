# TraceLeak NEXT TODO

Current checkpoint: Variable State Sequence Schema v1 implemented; proceed to dependency graph representation.

## Why this changed

The Level 20-26 index/checkpoint chain drifted away from the project objective. Those files are safe scaffolding, but they do not advance deep-learning-based program analysis.

TraceLeak's core objective is Deep Program Representation: learning from program events, variable state transitions, data/control dependencies, and evidence chains.

The inventory in `docs/core-modeling-inventory.md` shows that the current NN/MLP path is a token-count baseline and smoke-test layer, not the final architecture.

`traceleak/program_event_schema.py` now provides Program Event Schema v1 as the first schema-first normalization layer after legacy traces or legacy `model_sequence` steps.

`traceleak/variable_state_sequence.py` now provides Variable State Sequence Schema v1, including public-safe variable state validation and coarse read/write derivation from ProgramEvent records.

## Anti-drift rule

Do not create another Level N index-only checkpoint unless explicitly requested as maintenance.

A next task must directly advance at least one of:

- program event schema
- variable state sequence schema
- dependency graph schema
- deep model dataset builder
- sequence/graph model baseline
- attention/attribution export
- ablation/evidence chain
- OpenSSL metadata-to-model-sequence integration

## Validation baseline

```powershell
cd C:\Users\junny\Desktop\traceLeak\TraceLeak
git pull --ff-only
ruff check .
pytest
```

## Completed core reset tasks

- [x] Inventory existing MLP, attention, attribution, ablation, and evidence-chain modules.
- [x] Define Program Event Schema v1.
- [x] Define Variable State Sequence Schema v1.

## Immediate core task

- [ ] Define Dependency Graph Schema v1.

Minimum acceptable scope:

- add `traceleak/dependency_graph_schema.py`
- add `tests/test_dependency_graph_schema.py`
- add `docs/dependency-graph-schema-v1.md`
- define graph node fields:
  - `node_id`
  - `node_type`
  - `label`
  - `source_event_id`
  - `time_step`
  - `metadata`
- define graph edge fields:
  - `edge_id`
  - `edge_type`
  - `source_node_id`
  - `target_node_id`
  - `source_event_id`
  - `time_step`
  - `metadata`
- support node types:
  - `variable`
  - `operation`
  - `event`
  - `branch`
  - `memory_access`
  - `observable_output`
- support edge types:
  - `reads`
  - `writes`
  - `depends_on`
  - `controls`
  - `derives`
  - `observes`
- include a helper that can derive a coarse dependency graph from ProgramEvent and VariableStateRecord records
- keep raw secret values out of public-safe graph metadata

## Then

- [ ] Define Transformer/GNN-ready Deep Program Dataset Contract.
- [ ] Define attention/attribution output format for token, variable, event, and edge levels.
- [ ] Extend ablation from token-count drops to event, variable, edge, and timestep masks.

## References

```text
docs/core-roadmap-reset.md
docs/core-modeling-inventory.md
docs/program-event-schema-v1.md
docs/variable-state-sequence-v1.md
docs/next-session-handoff.md
```
