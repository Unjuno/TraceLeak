## Summary

Describe the change.

## Type of Change

- [ ] Documentation
- [ ] Schema or validation
- [ ] Trace view conversion
- [ ] Metrics or attribution
- [ ] Feature extraction
- [ ] Baseline evaluation
- [ ] Reporting
- [ ] Experiment config
- [ ] Tests
- [ ] Other

## Safety Review

- [ ] This PR does not commit private keys, raw traces, RNG state, DRBG state, memory dumps, or secret-equivalent material.
- [ ] Public examples are synthetic, redacted, path-only, metadata-only, or otherwise explicitly safe.
- [ ] The change does not make raw or cheat views part of the default public-safe workflow.
- [ ] The change does not add heavy local experiments to the default test path.

## Checks Run

- [ ] `pytest`
- [ ] `ruff check .`
- [ ] `python scripts/validate_trace.py --public examples/synthetic/synthetic_trace_sample.jsonl`
- [ ] `python scripts/validate_config.py experiments/exp_000_synthetic_leak/config.json`

## Notes

Add any design notes, limitations, or follow-up work.
