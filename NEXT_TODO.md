# TraceLeak NEXT TODO

Current checkpoint: core roadmap reset; Level index chain is stopped.

## Why this changed

The Level 20-26 index/checkpoint chain drifted away from the project objective. Those files are safe scaffolding, but they do not advance deep-learning-based program analysis.

TraceLeak's core objective is Deep Program Representation: learning from program events, variable state transitions, data/control dependencies, and evidence chains.

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

## Immediate core tasks

- [ ] Inventory existing MLP, attention, attribution, ablation, and evidence-chain modules.
- [ ] Define Program Event Schema v1.
- [ ] Define Variable State Sequence Schema v1.
- [ ] Define Dependency Graph Schema v1.
- [ ] Define Transformer-ready dataset contract.
- [ ] Define attention/attribution output format for token, variable, event, and edge levels.
- [ ] Replace Level-index continuation with a core deep-learning roadmap.

## Reference

```text
docs/core-roadmap-reset.md
```
