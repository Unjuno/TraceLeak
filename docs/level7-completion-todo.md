# Level 7 Completion TODO

Level 7 is the review-gated planning stage after Level 6 metadata-profile validation.

Current baseline: Level 6 is locally all pass. The reported local validation count is 610 passed. Level 7 must not automatically enable external execution, source-tree mutation, payload collection, raw capture, or evidence claims.

## Level 7 goal

Create a review-gated planning layer that can prepare the next research step without crossing into operational execution or claim-making.

The Level 7 flow is:

```text
Level 6 profile demo summary
  -> Level 7 review gate
  -> planning-only contract
  -> artifact boundary plan
  -> review checklist
  -> local readiness report
```

## Level 7 non-goals

- No external project build.
- No external project execution.
- No source tree mutation.
- No patch materialization.
- No raw capture collection.
- No payload collection.
- No private material collection.
- No runtime evidence claim.
- No vulnerability claim.

## Level 7 done definition

Level 7 is complete when all of the following are true:

- [x] Level 6 focused tests have passed locally.
- [x] Full local test suite has passed locally.
- [x] A Level 7 review gate exists.
- [ ] A planning-only contract exists and requires an explicit `approve_planning_only` gate.
- [ ] The planning contract forbids operational tasks by construction.
- [ ] An artifact boundary plan exists.
- [ ] The artifact boundary plan lists accepted future metadata artifact classes.
- [ ] The artifact boundary plan lists rejected artifact classes.
- [ ] A local review checklist exists.
- [ ] A local readiness report exists.
- [ ] A writer CLI exists only for Level 7 planning artifacts.
- [ ] Focused Level 7 tests pass.
- [ ] `ruff check .` passes.
- [ ] Full `pytest` passes.

## P107: planning-only contract

### Purpose

Create a contract that allows only planning artifact generation after a Level 7 review gate has approved `approve_planning_only`.

### Implementation tasks

- [ ] Add a planning-only contract helper.
- [ ] Require a valid Level 7 review gate.
- [ ] Require `decision = approve_planning_only`.
- [ ] Reject the default `defer` decision.
- [ ] Define allowed planning tasks:
  - [ ] metadata ingress review
  - [ ] artifact shape review
  - [ ] field allowlist review
  - [ ] validation command review
  - [ ] report surface review
- [ ] Define rejected task classes:
  - [ ] external build
  - [ ] external execution
  - [ ] source mutation
  - [ ] patch materialization
  - [ ] raw capture collection
  - [ ] payload collection
  - [ ] claim-making
- [ ] Emit JSON with conservative allowances:
  - [ ] planning only true
  - [ ] direct action false
  - [ ] source mutation false
  - [ ] payload collection false
  - [ ] claim false

### Tests

- [ ] Build contract from `approve_planning_only` gate.
- [ ] Reject contract from `defer` gate.
- [ ] Reject unknown planning task.
- [ ] Reject rejected task class.
- [ ] Validate JSON writer.

## P108: artifact boundary plan

### Purpose

Define what future local artifacts may be considered at Level 8 planning time without accepting raw or sensitive content.

### Implementation tasks

- [ ] Add artifact boundary plan helper.
- [ ] Require a valid planning-only contract.
- [ ] Define accepted future artifact classes:
  - [ ] profile JSON
  - [ ] adapter input JSON
  - [ ] model-sequence JSON
  - [ ] baseline result JSON
  - [ ] NN result JSON
  - [ ] summary JSON
  - [ ] Markdown report
- [ ] Define rejected artifact classes:
  - [ ] source text
  - [ ] command transcript
  - [ ] build log
  - [ ] execution log
  - [ ] raw trace bytes
  - [ ] payload dump
  - [ ] private material
- [ ] Define path constraints:
  - [ ] must be under `reports/local/`
  - [ ] no absolute paths
  - [ ] no parent traversal
- [ ] Define content-inspection rule:
  - [ ] path-only indexing is allowed
  - [ ] payload reading is not allowed unless separately approved in a later level

### Tests

- [ ] Build boundary plan from valid planning contract.
- [ ] Reject missing planning-only allowance.
- [ ] Reject rejected artifact class.
- [ ] Reject absolute or parent-traversal paths.
- [ ] Validate JSON writer.

## P109: Level 7 local review checklist

### Purpose

Create a checklist for human review before any later runtime-proximity work is even planned.

### Checklist items

- [ ] Confirm Level 6 profile demo summary exists.
- [ ] Confirm Level 7 review gate exists.
- [ ] Confirm planning-only decision is explicit.
- [ ] Confirm direct action remains disabled.
- [ ] Confirm source mutation remains disabled.
- [ ] Confirm payload collection remains disabled.
- [ ] Confirm claim-making remains disabled.
- [ ] Confirm accepted artifact classes are metadata/report only.
- [ ] Confirm rejected artifact classes include source text, command transcript, build log, execution log, raw capture, payload, and private material.
- [ ] Confirm full test suite has passed before moving further.

### Tests

- [ ] Checklist renders as JSON.
- [ ] Checklist renders as Markdown.
- [ ] Checklist rejects missing required item groups.

## P110: Level 7 readiness report

### Purpose

Summarize the Level 7 planning state in Markdown.

### Required sections

- [ ] Level 6 baseline status.
- [ ] Review gate status.
- [ ] Planning-only allowances.
- [ ] Artifact boundary.
- [ ] Rejected artifact classes.
- [ ] Local validation commands.
- [ ] Next-level preconditions.

### Tests

- [ ] Report contains required headings.
- [ ] Report states no external execution is authorized.
- [ ] Report states no source mutation is authorized.
- [ ] Report states no payload collection is authorized.
- [ ] Report states no claim is authorized.

## P111: Level 7 planning artifact writer CLI

### Purpose

Expose a writer for local planning artifacts only.

### Implementation tasks

- [ ] Add a neutral writer CLI name.
- [ ] Use only local JSON summary input.
- [ ] Write only planning artifacts.
- [ ] Do not execute external commands.
- [ ] Do not inspect raw payloads.
- [ ] Do not mutate source trees.
- [ ] Do not generate claims.

### Tests

- [ ] CLI writes planning contract.
- [ ] CLI writes artifact boundary plan.
- [ ] CLI writes review checklist.
- [ ] CLI writes readiness report.
- [ ] CLI rejects a gate without planning approval.

## P112: docs and handoff update

### Documentation tasks

- [ ] Update `docs/local-validation.md` with Level 7 focused commands.
- [ ] Update `docs/next-session-handoff.md` with Level 7 status.
- [ ] Update `NEXT_TODO.md` with Level 7 current checkpoint.
- [ ] Add Level 7 generation command.
- [ ] Add Level 7 validation command group.

## P113: Level 7 validation checkpoint

### Commands

```powershell
cd C:\Users\junny\Desktop\traceLeak\TraceLeak
git pull --ff-only
pytest tests/test_level7_review_gate.py
pytest tests/test_level7_planning_contract.py
pytest tests/test_level7_artifact_boundary_plan.py
pytest tests/test_level7_review_checklist.py
pytest tests/test_level7_readiness_report.py
pytest tests/test_write_level7_planning_artifacts_cli.py
ruff check .
pytest
```

### Completion criteria

- [ ] Focused Level 7 tests pass.
- [ ] `ruff check .` passes.
- [ ] Full `pytest` passes.
- [ ] Level 7 output artifacts stay under `reports/local/`.

## Recommended implementation order

1. P107 planning-only contract.
2. P108 artifact boundary plan.
3. P109 local review checklist.
4. P110 readiness report.
5. P111 writer CLI.
6. P112 docs and handoff update.
7. P113 validation checkpoint.

## Stop condition

Stop before any Level 8 work unless Level 7 focused tests, `ruff check .`, and full `pytest` all pass locally.
