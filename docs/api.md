# Public API Overview

TraceLeak exposes a small Python API for the lightweight public-safe workflow.

The command-line tools remain the primary interface, but these functions are available for integration tests, notebooks, and small local harnesses.

## Schema

```python
from traceleak import validate_run
```

Validates one TraceLeak run dictionary.

## Metrics

```python
from traceleak import delta_h, accuracy, top_k_recall
```

Core lightweight metrics:

- `delta_h(candidate_count, remaining_count)`
- `accuracy(y_true, y_pred)`
- `top_k_recall(y_true, y_topk)`

## Views

```python
from traceleak import to_view
```

Converts a validated run to `meta`, `path`, or `redacted` view.

## Features

```python
from traceleak import extract_feature_vector
```

Extracts a sparse numeric feature dictionary from one public-safe run.

## Attribution

```python
from traceleak import AttributionScore, ablation_drop
```

Computes lightweight ablation contribution scores.

## Config

```python
from traceleak import validate_config
```

Validates experiment config dictionaries.

## Workflow

```python
from traceleak import run_lightweight_experiment

result = run_lightweight_experiment(
    "experiments/exp_000_synthetic_leak/config.json",
    out_dir="reports/local",
)

for path in result.written_paths:
    print(path)
```

This runs the config-driven lightweight workflow:

```text
config validation
  -> public trace validation
  -> feature export
  -> baseline evaluation
  -> attribution report generation
```

## Stability

The public API is pre-alpha. Names may change before the first stable release.

Scripts under `scripts/` are considered operational examples and may change more frequently than the package API.
