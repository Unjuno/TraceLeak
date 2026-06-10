# Release Checklist

This checklist is for public-safe TraceLeak releases.

## Pre-Release Checks

- [ ] `pytest` passes.
- [ ] `ruff check .` passes.
- [ ] Synthetic trace sample validates with `--public`.
- [ ] Experiment config validates.
- [ ] Generated local files are not staged.
- [ ] No raw traces are staged.
- [ ] No private keys or secret-equivalent files are staged.
- [ ] README reflects current capabilities.
- [ ] ROADMAP reflects current status.
- [ ] SECURITY.md is still accurate.

## Local Commands

```bash
pytest
ruff check .
python scripts/validate_trace.py --public examples/synthetic/synthetic_trace_sample.jsonl
python scripts/validate_config.py experiments/exp_000_synthetic_leak/config.json
python scripts/run_experiment.py experiments/exp_000_synthetic_leak/config.json
```

PowerShell:

```powershell
pytest
ruff check .
python scripts/validate_trace.py --public examples/synthetic/synthetic_trace_sample.jsonl
python scripts/validate_config.py experiments/exp_000_synthetic_leak/config.json
python scripts/run_experiment.py experiments/exp_000_synthetic_leak/config.json
```

## Git Safety Review

```bash
git status --short
git diff --cached --name-only
```

Review staged files before release.

Do not release if staged files include:

- raw traces;
- private keys;
- generator state;
- memory dumps;
- production traces;
- large local artifacts.

## Versioning

For pre-alpha releases, use:

```text
v0.1.0-alpha.N
```

A release should include:

- summary;
- public-safe scope;
- new modules or scripts;
- known limitations;
- safety notes;
- next milestone.

## Post-Release

- [ ] Confirm package metadata.
- [ ] Confirm repository files render correctly.
- [ ] Confirm examples remain public-safe.
- [ ] Open follow-up issues for incomplete roadmap items.
