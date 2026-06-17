# TraceLeak NEXT TODO

Current checkpoint: core modeling inventory complete; proceed to schema-first Deep Program Representation.

## Why this changed

The Level 20-26 index/checkpoint chain drifted away from the project objective. Those files are safe scaffolding, but they do not advance deep-learning-based program analysis.

TraceLeak's core objective is Deep Program Representation: learning from program events, variable state transitions, data/control dependencies, and evidence chains.

The inventory in `docs/core-modeling-inventory.md` shows that the current NN/MLP path is a token-count baseline and smoke-test layer, not the final architecture.

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

## Immediate core task

- [ ] Define Program Event Schema v1.

Minimum acceptable scope:

- add `traceleak/program_event_schema.py`
- add `tests/test_program_event_schema.py`
- add `docs/program-event-schema-v1.md`
- define normalized event fields:
  - `event_id`
  - `time_step`
  - `event_type`
  - `operation`
  - `function`
  - `source_location`
  - `variable_reads`
  - `variable_writes`
  - `value_class`
  - `dependency_tags`
  - `control_context`
  - `metadata`
- include a compatibility adapter from legacy `model_features.py` model steps where safe
- keep raw secret fields out of public-safe events

## Then

- [ ] Define Variable State Sequence Schema v1.
- [ ] Define Dependency Graph Schema v1.
- [ ] Define Transformer/GNN-ready Deep Program Dataset Contract.
- [ ] Define attention/attribution output format for token, variable, event, and edge levels.
- [ ] Extend ablation from token-count drops to event, variable, edge, and timestep masks.

## References

```text
docs/core-roadmap-reset.md
docs/core-modeling-inventory.md
docs/next-session-handoff.md
```
