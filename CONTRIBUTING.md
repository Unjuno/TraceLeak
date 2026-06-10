# Contributing to TraceLeak

TraceLeak is a defensive research framework for source-level leakage assessment of cryptographic implementations.

Contributions should preserve the project's safety boundary and public-safe workflow.

## Development Setup

```bash
git clone https://github.com/Unjuno/TraceLeak.git
cd TraceLeak
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
pytest
```

Windows PowerShell:

```powershell
git clone https://github.com/Unjuno/TraceLeak.git
cd TraceLeak
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
pytest
```

## Expected Checks

Before opening a pull request, run:

```bash
pytest
ruff check .
python scripts/validate_trace.py --public examples/synthetic/synthetic_trace_sample.jsonl
python scripts/validate_config.py experiments/exp_000_synthetic_leak/config.json
```

## Safety Rules

Do not commit:

- private keys;
- raw traces;
- RNG or DRBG state;
- raw prime candidates;
- private factors;
- memory dumps;
- production traces;
- secret-equivalent local artifacts.

Public examples must be synthetic, redacted, path-only, metadata-only, or otherwise explicitly safe.

## Contribution Areas

Good first contribution areas:

- schema validation;
- trace view conversion;
- redaction helpers;
- feature extraction;
- baseline evaluation;
- reporting;
- documentation;
- synthetic examples;
- tests.

Heavy local experiments and neural training should remain optional and must not become part of the default test path.

## Claim Discipline

TraceLeak reports should distinguish:

- raw-only upper-bound measurements;
- redacted trace signal;
- path or observable signal;
- source-localized signal;
- patch-verified signal.

A contribution should not overstate results or frame lab-only measurements as general impact.

## Pull Request Checklist

A pull request should state:

- what changed;
- which files were added or modified;
- whether the change touches safety-sensitive code paths;
- which local checks were run;
- whether any generated files are intentionally committed.
