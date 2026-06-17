# TraceLeak Core Roadmap Reset

This document resets the project direction after the Level index/checkpoint chain drifted away from the core research goal.

## Why the work drifted

The recent Level 20-26 work repeatedly generated path-only index helpers, reports, writer CLIs, and TODO checkpoints. That work was safe and testable, but it mostly managed outputs from the previous level. It did not advance the core TraceLeak objective.

The drift happened because the implementation loop optimized for low-risk, local-testable scaffolding instead of the research target: deep-learning-based program-state analysis.

## Core project objective

TraceLeak is not primarily a TODO/index generator. TraceLeak is a deep-learning program-analysis project.

The core objective is to represent program execution as learnable structure and train deep models to identify which internal program states, variable updates, operations, dependencies, and execution events carry useful leakage or behavior signals.

## Correct framing

MLP is an early smoke-test baseline. It is not the intended final modeling approach.

MLP can answer limited questions:

- Does the current feature representation contain any predictive signal?
- Does the data pipeline train at all?
- Does the label construction expose a measurable signal?
- Does a simple baseline beat random or trivial heuristics?

MLP should not be treated as sufficient for program understanding. Program analysis requires sequence, graph, and state-transition modeling.

## Target modeling direction

The next core direction is Deep Program Representation:

- Program Event Schema: assignment, load, store, branch, call, return, arithmetic, compare, crypto step.
- Variable State Sequence: variable identity, value class, dependency class, update time, source location.
- Data/control dependency graph: edges between variables, operations, branch conditions, and observable events.
- Sequence models: Transformer or temporal encoder for ordered execution events.
- Graph models: graph encoder for dependency/data-flow structure.
- Hybrid model: sequence encoder plus graph encoder plus metadata embeddings.
- Explanation layer: attention, attribution, ablation, counterfactual masking, token/variable/event importance.

## Anti-drift rules

Do not create another Level N index-only checkpoint unless the user explicitly asks for that exact maintenance task.

Do not continue the pattern:

```text
Level N index -> Level N+1 index -> Level N+2 index
```

A next task must directly advance at least one of these core items:

- program event schema
- variable state sequence schema
- dependency graph schema
- deep model dataset builder
- sequence/graph model baseline
- attention/attribution export
- ablation/evidence chain
- OpenSSL metadata-to-model-sequence integration

If a proposed task only records paths to prior outputs, it is not core work and should be stopped.

## Immediate next TODO

Replace the Level-index chain with a core roadmap checkpoint:

1. Inventory existing MLP, attention, attribution, ablation, and evidence-chain modules.
2. Define Program Event Schema v1.
3. Define Variable State Sequence Schema v1.
4. Define Dependency Graph Schema v1.
5. Define a Transformer-ready dataset contract.
6. Define attention/attribution output format at token, variable, event, and edge levels.
7. Update `NEXT_TODO.md` to point to these core tasks instead of another Level index.
