# Symbolic metadata schema

This schema is for small public-safe metadata examples used by the local demo chain.

## Required top-level fields

- `format`: must be `traceleak.openssl_derived_metadata_input.v1`
- `source_pin_digest`: symbolic digest string
- `target_decision`: must be `constant_time_helper_misuse_path`
- `metadata_only`: must be `true`
- `payload_free`: must be `true`
- `records`: non-empty list

## Required record fields

- `source_region_token`: symbolic region token
- `transition_token`: symbolic transition token
- `label`: lab-only label used for demo checks

## Minimal example

```json
{
  "format": "traceleak.openssl_derived_metadata_input.v1",
  "source_pin_digest": "sha256:source-pin",
  "target_decision": "constant_time_helper_misuse_path",
  "metadata_only": true,
  "payload_free": true,
  "records": [
    {
      "source_region_token": "ct_helper_family_a",
      "transition_token": "branch_symbolic_a",
      "label": "bucket_a"
    },
    {
      "source_region_token": "ct_helper_family_b",
      "transition_token": "branch_symbolic_b",
      "label": "bucket_b"
    }
  ]
}
```

## Local validation

```powershell
cd C:\Users\junny\Desktop\traceLeak\TraceLeak
pytest tests/test_openssl_derived_metadata_adapter.py tests/test_adapt_openssl_derived_metadata_cli.py
```
