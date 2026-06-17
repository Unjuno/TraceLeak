# TraceLeak NEXT TODO

Current checkpoint: Deep Program Dataset Contract v1 implemented; proceed to Attention / Attribution Export Format v1.

## Why this changed

The Level 20-26 index/checkpoint chain drifted away from the project objective. Those files are safe scaffolding, but they do not advance deep-learning-based program analysis.

TraceLeak's core objective is Deep Program Representation: learning from program events, variable state transitions, data/control dependencies, and evidence chains.

The inventory in `docs/core-modeling-inventory.md` shows that the current NN/MLP path is a token-count baseline and smoke-test layer, not the final architecture.

`traceleak/program_event_schema.py` now provides Program Event Schema v1 as the first schema-first normalization layer after legacy traces or legacy `model_sequence` steps.

`traceleak/variable_state_sequence.py` now provides Variable State Sequence Schema v1, including public-safe variable state validation and coarse read/write derivation from ProgramEvent records.

`traceleak/dependency_graph_schema.py` now provides Dependency Graph Schema v1, including public-safe node/edge validation and coarse graph derivation from ProgramEvent plus VariableStateRecord records.

`traceleak/deep_program_dataset.py` now provides Deep Program Dataset Contract v1, including sequence/graph/hybrid consumer masks and lab-only label separation.

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
- [x] Define Dependency Graph Schema v1.
- [x] Define Transformer/GNN-ready Deep Program Dataset Contract v1.

## Immediate core task

- [ ] Define Attention / Attribution Export Format v1.

Minimum acceptable scope:

- add `traceleak/attribution_export_schema.py`
- add `tests/test_attribution_export_schema.py`
- add `docs/attention-attribution-export-format-v1.md`
- define attribution/export fields:
  - `sample_id`
  - `model_id`
  - `model_family`
  - `attribution_level`
  - `entity_id`
  - `entity_type`
  - `score`
  - `rank`
  - `method`
  - `evidence`
  - `metadata`
- support levels:
  - `token`
  - `event`
  - `variable`
  - `graph_node`
  - `graph_edge`
- distinguish attention weights from causal attribution
- include public-safe evidence and metadata validation
- keep raw secret values out of public-safe attribution metadata

## Then

- [ ] Extend ablation from token-count drops to event, variable, edge, and timestep masks.
- [ ] Add sequence/graph/hybrid model baseline entry points after the dataset contract exists.
- [ ] Add tensorization contract for sequence and graph consumers.

## References

```text
docs/core-roadmap-reset.md
docs/core-modeling-inventory.md
docs/program-event-schema-v1.md
docs/variable-state-sequence-v1.md
docs/dependency-graph-schema-v1.md
docs/deep-program-dataset-contract-v1.md
docs/next-session-handoff.md
```
