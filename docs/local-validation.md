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

## Symbolic metadata demo chain validation

```powershell
pytest tests/test_symbolic_metadata_demo_chain.py
pytest tests/test_run_symbolic_metadata_demo_chain_cli.py
pytest tests/test_metadata_symbolic_authoring.py tests/test_build_metadata_symbolic_input_cli.py
```

## Demo summary comparison validation

```powershell
pytest tests/test_demo_summary_comparison.py
pytest tests/test_compare_demo_summaries_cli.py
pytest tests/test_symbolic_metadata_demo_chain.py tests/test_run_symbolic_metadata_demo_chain_cli.py
```

## Local demo dashboard validation

```powershell
pytest tests/test_local_demo_dashboard.py
pytest tests/test_write_local_demo_dashboard_cli.py
pytest tests/test_demo_summary_comparison.py tests/test_compare_demo_summaries_cli.py
```

## Local report bundle validation

```powershell
pytest tests/test_local_report_bundle.py
pytest tests/test_write_local_report_bundle_cli.py
pytest tests/test_local_demo_dashboard.py tests/test_write_local_demo_dashboard_cli.py
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

## Run authored symbolic metadata demo chain

```powershell
traceleak-run-symbolic-metadata-demo-chain --out-dir reports/local/symbolic_metadata_demo --epochs 20 --write-report
```

## Compare metadata and symbolic demo summaries

```powershell
traceleak-compare-demo-summaries --metadata-summary reports/local/openssl_metadata_demo/demo-summary.json --symbolic-summary reports/local/symbolic_metadata_demo/symbolic-demo-summary.json --out reports/local/demo-summary-comparison.json --markdown-out reports/local/demo-summary-comparison.md
```

## Build combined local dashboard

```powershell
traceleak-write-local-demo-dashboard --root-dir reports/local --out reports/local/local-demo-dashboard.json --markdown-out reports/local/local-demo-dashboard.md
```

## Build one-command local report bundle

```powershell
traceleak-write-local-report-bundle --root-dir reports/local --record-count 4 --epochs 20
```

## Render local Markdown summary from existing JSON

```powershell
traceleak-metadata-demo-markdown-summary --summary reports/local/openssl_metadata_demo/demo-summary.json --manifest reports/local/openssl_metadata_demo/demo-manifest.json --out reports/local/openssl_metadata_demo/demo-summary.md
```

Generated files should stay under `reports/local/`.
