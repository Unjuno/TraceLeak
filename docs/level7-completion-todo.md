# Level 7 Completion TODO

Level 7 is the review-gated planning stage after Level 6 metadata-profile validation.

Current baseline: Level 6 and Level 7 are locally reported all pass. Level 7 does not enable external execution, source-tree mutation, payload collection, raw capture, or evidence claims.

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
- [x] A planning-only contract exists and requires an explicit `approve_planning_only` gate.
- [x] The planning contract forbids operational tasks by construction.
- [x] An artifact boundary plan exists.
- [x] The artifact boundary plan lists accepted future metadata artifact classes.
- [x] The artifact boundary plan lists rejected artifact classes.
- [x] A local review checklist exists.
- [x] A local readiness report exists.
- [x] A writer CLI exists only for Level 7 planning artifacts.
- [x] Focused Level 7 tests pass.
- [x] `ruff check .` passes.
- [x] Full `pytest` passes.

## P107: planning-only contract

### Status

- [x] Added planning-only contract helper.
- [x] Required a valid Level 7 review gate.
- [x] Required `decision = approve_planning_only`.
- [x] Rejected the default `defer` decision.
- [x] Defined allowed planning tasks.
- [x] Defined rejected task classes.
- [x] Emitted JSON with conservative allowances.
- [x] Added focused tests.

## P108: artifact boundary plan

### Status

- [x] Added artifact boundary plan helper.
- [x] Required a valid planning-only contract.
- [x] Defined accepted future artifact classes.
- [x] Defined rejected artifact classes.
- [x] Defined path constraints under `reports/local/`.
- [x] Defined path-only content rule.
- [x] Added focused tests.

## P109: Level 7 local review checklist

### Status

- [x] Added local review checklist helper.
- [x] Confirmed Level 6 summary, review gate, planning-only decision, disabled direct action, disabled source mutation, disabled payload collection, disabled claim-making, accepted metadata/report artifacts, rejected raw/sensitive artifacts, and local all-pass requirement.
- [x] Added focused tests.

## P110: Level 7 readiness report

### Status

- [x] Added readiness Markdown renderer.
- [x] Included Level 6 baseline status.
- [x] Included review gate status.
- [x] Included planning-only allowances.
- [x] Included artifact boundary.
- [x] Included rejected artifact classes.
- [x] Included local validation commands.
- [x] Included next-level preconditions.
- [x] Added focused tests.

## P111: Level 7 planning artifact writer CLI

### Status

- [x] Added neutral writer CLI name: `traceleak-write-level7-artifacts`.
- [x] Wrote only local planning artifacts.
- [x] Did not execute external commands.
- [x] Did not inspect raw payloads.
- [x] Did not mutate source trees.
- [x] Did not generate claims.
- [x] Added focused tests.

## P112: docs and handoff update

### Status

- [x] Updated `docs/local-validation.md` with Level 7 focused commands.
- [x] Updated `docs/next-session-handoff.md` with Level 7 status.
- [x] Updated `NEXT_TODO.md` with Level 7 current checkpoint.
- [x] Added Level 7 generation command.
- [x] Added Level 7 validation command group.

## P113: Level 7 validation checkpoint

### Status

- [x] Focused Level 7 tests reported all pass locally.
- [x] `ruff check .` reported pass locally.
- [x] Full `pytest` reported pass locally.
- [x] Level 7 output artifacts stay under `reports/local/`.

## Next block

Level 8 should be approved metadata artifact intake: path-only local artifact intake for already-approved metadata/report classes under `reports/local/`.

## Stop condition

Do not move into external build, external run, source mutation, raw capture, payload collection, private material collection, or claim generation from Level 7. Level 8 must remain path-only metadata/report artifact intake unless a later explicit review gate changes the boundary.
