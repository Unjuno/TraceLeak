# Next session handoff

Current checkpoint: P93-P95 one-command local report bundle implemented; local validation pending.

## Local validation

```powershell
cd C:\Users\junny\Desktop\traceLeak\TraceLeak
git pull --ff-only
ruff check .
pytest
```

## Focused checks

```powershell
pytest tests/test_local_report_bundle.py
pytest tests/test_write_local_report_bundle_cli.py
pytest tests/test_local_demo_dashboard.py
pytest tests/test_write_local_demo_dashboard_cli.py
pytest tests/test_demo_summary_comparison.py
pytest tests/test_compare_demo_summaries_cli.py
pytest tests/test_symbolic_metadata_demo_chain.py
pytest tests/test_run_symbolic_metadata_demo_chain_cli.py
pytest tests/test_metadata_symbolic_authoring.py
pytest tests/test_build_metadata_symbolic_input_cli.py
pytest tests/test_openssl_runtime_transition_gate.py tests/test_validate_openssl_runtime_transition_gate_cli.py
pytest tests/test_openssl_derived_metadata_adapter.py tests/test_adapt_openssl_derived_metadata_cli.py
pytest tests/test_metadata_demo_artifact_index.py
pytest tests/test_metadata_demo_readme_snippet.py
pytest tests/test_metadata_demo_metrics.py
pytest tests/test_metadata_demo_markdown_summary.py tests/test_metadata_demo_markdown_summary_cli.py
pytest tests/test_run_openssl_metadata_demo_chain_cli.py
pytest tests/test_openssl_metadata_demo_chain_outputs.py
```

## What changed in this block

- Added Level 5 to Level 6 TODO document.
- Added one-command local report bundle helper.
- Added local report bundle summary and validation.
- Added CLI to write the local report bundle.
- Registered `traceleak-write-local-report-bundle` entry point.
- Updated local validation docs with bundle generation commands.

## Local report bundle command

```powershell
traceleak-write-local-report-bundle --root-dir reports/local --record-count 4 --epochs 20
```

## Next likely work

- Fix any local test failures first.
- If all pass, start Level 6 with an OpenSSL-derived metadata ingestion profile.
- Keep Level 6 metadata-only and payload-free at the ingress boundary.
- Do not introduce OpenSSL build, run, source patch, or raw capture steps in the first Level 6 block.
