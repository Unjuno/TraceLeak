# TraceLeak NEXT TODO

Current checkpoint: Program Event Schema v1 implemented; proceed to variable-state representation.

## Why this changed

The Level 20-26 index/checkpoint chain drifted away from the project objective. Those files are safe scaffolding, but they do not advance deep-learning-based program analysis.

TraceLeak's core objective is Deep Program Representation: learning from program events, variable state transitions, data/control dependencies, and evidence chains.

The inventory in `docs/core-modeling-inventory.md` shows that the current NN/MLP path is a token-count baseline and smoke-test layer, not the final architecture.

`traceleak/program_event_schema.py` now provides Program Event Schema v1 as the first schema-first normalization layer after legacy traces or legacy `model_sequence` steps.

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

## Immediate core task

- [ ] Define Variable State Sequence Schema v1.

Minimum acceptable scope:

- add `traceleak/variable_state_sequence.py`
- add `tests/test_variable_state_sequence.py`
- add `docs/variable-state-sequence-v1.md`
- define normalized variable-state fields:
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
- include a helper that can derive coarse state records from ProgramEvent records when reads/writes exist
- keep raw secret values out of public-safe state records

## Then

- [ ] Define Dependency Graph Schema v1.
- [ ] Define Transformer/GNN-ready Deep Program Dataset Contract.
- [ ] Define attention/attribution output format for token, variable, event, and edge levels.
- [ ] Extend ablation from token-count drops to event, variable, edge, and timestep masks.

## References

```text
docs/core-roadmap-reset.md
docs/core-modeling-inventory.md
docs/program-event-schema-v1.md
docs/next-session-handoff.md
```
