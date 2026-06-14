# Local validation

Run commands from the repository root.

```powershell
cd C:\Users\junny\Desktop\traceLeak\TraceLeak
```

## Full validation

```powershell
git pull --ff-only
ruff check .
pytest
```

## Focused metadata chain validation

```powershell
ruff check .
pytest tests/test_openssl_model_sequence_metadata_sample.py tests/test_build_openssl_model_sequence_metadata_sample_cli.py
pytest tests/test_openssl_model_sequence_metadata_sample_model_preflight.py tests/test_build_openssl_model_sequence_metadata_sample_model_preflight_cli.py
pytest tests/test_run_openssl_model_sequence_metadata_sample_demo_cli.py
pytest tests/test_run_openssl_metadata_demo_chain_cli.py
pytest tests/test_openssl_metadata_demo_chain_outputs.py
```

## Focused hardening validation

```powershell
pytest tests/test_openssl_model_sequence_metadata_demo_manifest.py tests/test_validate_openssl_model_sequence_metadata_demo_manifest_cli.py
pytest tests/test_openssl_runtime_transition_gate.py tests/test_validate_openssl_runtime_transition_gate_cli.py
pytest tests/test_openssl_derived_metadata_adapter.py tests/test_adapt_openssl_derived_metadata_cli.py
pytest tests/test_metadata_demo_token_ranking.py
pytest tests/test_openssl_metadata_demo_fixtures.py
```

## Markdown summary validation

```powershell
pytest tests/test_metadata_demo_markdown_summary.py tests/test_metadata_demo_markdown_summary_cli.py
pytest tests/test_run_openssl_metadata_demo_chain_cli.py
```

## Metrics export validation

```powershell
pytest tests/test_metadata_demo_metrics.py
pytest tests/test_run_openssl_metadata_demo_chain_cli.py
```

## Local artifact ergonomics validation

```powershell
pytest tests/test_metadata_demo_artifact_index.py
pytest tests/test_metadata_demo_readme_snippet.py
pytest tests/test_run_openssl_metadata_demo_chain_cli.py
```

## Symbolic metadata authoring validation

```powershell
pytest tests/test_metadata_symbolic_authoring.py
pytest tests/test_build_metadata_symbolic_input_cli.py
pytest tests/test_openssl_derived_metadata_adapter.py tests/test_adapt_openssl_derived_metadata_cli.py
```

## Shared fixture validation

```powershell
pytest tests/test_openssl_model_sequence_metadata_demo_manifest.py tests/test_metadata_demo_token_ranking.py tests/test_openssl_metadata_demo_chain_outputs.py
```

## Generate local demo JSON artifacts

```powershell
traceleak-run-openssl-metadata-demo-chain --out-dir reports/local/openssl_metadata_demo --record-count 4 --epochs 20
```

## Generate local demo JSON artifacts and Markdown

```powershell
traceleak-run-openssl-metadata-demo-chain --out-dir reports/local/openssl_metadata_demo --record-count 4 --epochs 20 --write-markdown-summary
```

## Generate Markdown with ranking table

```powershell
traceleak-run-openssl-metadata-demo-chain --out-dir reports/local/openssl_metadata_demo --record-count 4 --epochs 20 --write-markdown-summary --include-ranking
```

## Generate JSON, Markdown, metrics, and local index exports

```powershell
traceleak-run-openssl-metadata-demo-chain --out-dir reports/local/openssl_metadata_demo --record-count 4 --epochs 20 --write-markdown-summary --include-ranking --write-metrics-json --write-metrics-csv --write-artifact-index-json --write-artifact-index-markdown --write-command-snippet
```

## Build authored symbolic metadata input

```powershell
traceleak-build-metadata-symbolic-input --out reports/local/openssl_metadata_demo/symbolic-metadata-input.json
```

## Adapt authored symbolic metadata input

```powershell
traceleak-validate-openssl-runtime-transition-gate --out reports/local/openssl_metadata_demo/runtime-gate.json --reviewer reviewer --reviewed-at 2026-06-14T00:00:00Z
traceleak-adapt-openssl-derived-metadata --metadata reports/local/openssl_metadata_demo/symbolic-metadata-input.json --runtime-gate reports/local/openssl_metadata_demo/runtime-gate.json --out reports/local/openssl_metadata_demo/symbolic-model-sequence.json
```

## Render local Markdown summary from existing JSON

```powershell
traceleak-metadata-demo-markdown-summary --summary reports/local/openssl_metadata_demo/demo-summary.json --manifest reports/local/openssl_metadata_demo/demo-manifest.json --out reports/local/openssl_metadata_demo/demo-summary.md
```

Generated files should stay under `reports/local/`.
