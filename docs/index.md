# TraceLeak Documentation

This index lists the main public-safe documentation files.

## Project and Safety

- [Design](design.md)
- [Threat Model](threat_model.md)
- [Safety Boundary](safety_boundary.md)
- [Trace Schema](trace_schema.md)
- [Local Workflow](local_workflow.md)

## Lightweight Workflow

- [Feature Extraction](features.md)
- [Baseline Evaluation](baselines.md)
- [Reporting Workflow](reporting.md)
- [Experiment Configuration](experiments.md)
- [Model Result Files](model_results.md)
- [Public API Overview](api.md)

## Targets

- [Toy RSA-Like Target Design](toy_rsa_like_target.md)

## Repository-Level Files

- [README](../README.md)
- [Security Policy](../SECURITY.md)
- [Contributing](../CONTRIBUTING.md)
- [Roadmap](../ROADMAP.md)
- [Third-Party Notices](../THIRD_PARTY_NOTICES.md)

## Public-Safe Flow

```text
trace JSONL
  -> validate_trace.py
  -> convert_view.py
  -> extract_features.py
  -> evaluate_baseline.py
  -> make_report.py
  -> validate_model_result.py
  -> run_experiment.py
```

## Local-Only Boundary

The following remain local-only unless safely redacted or converted:

- raw traces;
- private keys;
- random generator state;
- memory dumps;
- large model checkpoints;
- heavy experiment artifacts.
