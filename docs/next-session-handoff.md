# Next session handoff

Current checkpoint: P31-P40 hardening block implemented as a public-safe metadata demo path.

## Local validation

```powershell
cd C:\Users\junny\Desktop\traceLeak\TraceLeak
git pull --ff-only
ruff check .
pytest
```

## Focused checks

```powershell
pytest tests/test_openssl_model_sequence_metadata_demo_manifest.py tests/test_validate_openssl_model_sequence_metadata_demo_manifest_cli.py
pytest tests/test_openssl_runtime_transition_gate.py tests/test_validate_openssl_runtime_transition_gate_cli.py
pytest tests/test_openssl_derived_metadata_adapter.py tests/test_adapt_openssl_derived_metadata_cli.py
pytest tests/test_metadata_demo_token_ranking.py
pytest tests/test_run_openssl_metadata_demo_chain_cli.py
pytest tests/test_openssl_metadata_demo_fixtures.py
```

## Next likely work

- Fix any local test failures first.
- If all pass, improve docs with small safe patches.
- Keep generated demo artifacts under `reports/local/`.
- Do not broaden beyond symbolic metadata until the checked-in validation path is stable.
