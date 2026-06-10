# Feature Extraction

TraceLeak converts validated trace runs into lightweight feature vectors before local modeling.

This layer is intentionally dependency-free. It does not use NumPy, Pandas, scikit-learn, PyTorch, or TensorFlow. Heavy local experiments may replace or extend this layer.

## Purpose

Feature extraction provides a stable interface between trace collection and local modeling:

```text
TraceLeak JSONL trace
  -> schema validation
  -> view conversion, if needed
  -> sparse feature vector
  -> local baseline model or NN
```

## Safety Boundary

By default, feature extraction refuses `raw` and `cheat` views.

```text
raw / cheat -> rejected unless --allow-raw is explicitly used
```

This prevents accidental featurization of raw secret-equivalent traces during normal public-safe workflows.

## JSON Output

```bash
python scripts/extract_features.py \
  --in examples/synthetic/synthetic_trace_sample.jsonl \
  --out features.json
```

PowerShell:

```powershell
python scripts/extract_features.py --in examples/synthetic/synthetic_trace_sample.jsonl --out features.json
```

The output is a list of run-level feature objects:

```json
[
  {
    "run_id": "synthetic_000001",
    "target": "synthetic-leak",
    "view": "redacted",
    "features": {
      "run.view=redacted": 1.0,
      "event_type=branch": 1.0
    }
  }
]
```

## CSV Output

```bash
python scripts/extract_features.py \
  --in examples/synthetic/synthetic_trace_sample.jsonl \
  --out features.csv \
  --format csv
```

PowerShell:

```powershell
python scripts/extract_features.py --in examples/synthetic/synthetic_trace_sample.jsonl --out features.csv --format csv
```

CSV output is intended for quick inspection or small baseline models.

For large experiments, a sparse matrix format should be added later.

## Feature Types

The default extractor emits:

| Feature | Meaning |
|---|---|
| `run.view=<view>` | Trace view |
| `run.target=<target>` | Target name |
| `run.target_version=<version>` | Target version |
| `event_type=<type>` | Event type count |
| `phase=<phase>` | Phase count |
| `function=<function>` | Function count |
| `file=<file>` | Source file count |
| `location=<file>:<line>` | Source location count |
| `event=<type>:<phase>:<function>:<name>` | Source-level event identity |
| `event_value:...` | Encoded redacted value feature |

## Local Output Policy

Local feature exports are ignored by default when written to:

```text
/features.json
/features.csv
features/local/
*.features.json
*.features.csv
```

Feature files intended for public examples should be placed under `examples/` and must not include raw or secret-equivalent values.

## Heavy Local Modeling

The repository does not run neural training by default.

A local modeling workflow may consume `features.json` or `features.csv`, but large model checkpoints, raw traces, and experiment outputs should remain outside version control.
