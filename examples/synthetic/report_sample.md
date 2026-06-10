# TraceLeak Attribution Report

- Target: `synthetic-example`
- View: `redacted`
- Metric: `DeltaH`
- Score: `10.0`

## Top Attribution Scores

| Rank | Group | Type | Contribution | Location | Evidence |
|---:|---|---|---:|---|---|
| 1 | `example_branch_event` | `mixed` | 6 | `examples/synthetic/target.c:21` | ablation |
| 2 | `example_loop_event` | `mixed` | 2.5 | `examples/synthetic/target.c:30` | ablation |
| 3 | `example_phase_event` | `mixed` | 1 | `examples/synthetic/target.c:10` | ablation |

## Notes

- Synthetic sample for validating report generation.
- This file does not contain raw trace data or secret-equivalent material.
