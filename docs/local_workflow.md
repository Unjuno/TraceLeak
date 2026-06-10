# Local Workflow

This document describes the lightweight local workflow for TraceLeak.

Heavy experiments such as OpenSSL instrumentation, raw trace generation, and NN training are intentionally kept local. The public repository provides the lightweight schema, safety, conversion, and validation infrastructure.

## Bootstrap

```bash
git clone https://github.com/Unjuno/TraceLeak.git
cd TraceLeak
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest
```

Or use the helper script:

```bash
bash scripts/bootstrap_local.sh
```

## Validate a Trace

```bash
python scripts/validate_trace.py examples/synthetic/synthetic_trace_sample.jsonl
```

For public-export safety checks:

```bash
python scripts/validate_trace.py --public examples/synthetic/synthetic_trace_sample.jsonl
```

## Convert Trace Views

```bash
python scripts/convert_view.py \
  --view path \
  --in local_raw_trace.jsonl \
  --out local_path_trace.jsonl
```

```bash
python scripts/convert_view.py \
  --view redacted \
  --in local_raw_trace.jsonl \
  --out local_redacted_trace.jsonl
```

```bash
python scripts/convert_view.py \
  --view meta \
  --in local_raw_trace.jsonl \
  --out local_meta_trace.jsonl
```

## Do Not Commit Local Experiment Outputs

The following should remain local:

- raw traces;
- raw OpenSSL traces;
- private factors;
- private keys;
- RNG or DRBG state;
- memory dumps;
- NN training outputs;
- large experiment artifacts.

The repository `.gitignore` is configured to reject common experiment outputs, but researchers must still review files before committing.

## Lightweight Commands

```bash
pytest
python scripts/validate_trace.py --public examples/synthetic/synthetic_trace_sample.jsonl
```

## Heavy Local-Only Work

The following work is expected to happen locally and is not part of the default bootstrap flow:

- OpenSSL source checkout and instrumentation builds;
- raw trace generation;
- raw-to-redacted conversion of sensitive traces;
- neural model training;
- large experiment execution;
- hardware-specific side-channel measurements.
