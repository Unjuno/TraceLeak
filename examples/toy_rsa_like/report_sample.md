# TraceLeak Attribution Report

- Target: `toy-rsa-like`
- View: `redacted`
- Metric: `DeltaH`
- Score: `6.0`

## Top Attribution Scores

| Rank | Group | Type | Contribution | Location | Evidence |
|---:|---|---|---:|---|---|
| 1 | `candidate_result` | `mixed` | 4 | `examples/toy_rsa_like/target.py:35` | ablation |
| 2 | `small_divisor_check` | `mixed` | 2 | `examples/toy_rsa_like/target.py:29` | ablation |
| 3 | `oddness_check` | `mixed` | 1 | `examples/toy_rsa_like/target.py:25` | ablation |
| 4 | `candidate_generated` | `mixed` | 0.5 | `examples/toy_rsa_like/target.py:21` | ablation |

## Notes

- Toy RSA-like synthetic ablation sample.
- No raw candidate values are included.
