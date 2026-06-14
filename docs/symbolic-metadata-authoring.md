# Symbolic metadata authoring

This page documents the local metadata-only authoring path.

The authored JSON is intended for the existing derived metadata adapter. It does not contain source text, command text, build output, execution output, raw capture, or runtime payload.

## Minimal record fields

Each record needs:

- `source_region_token`
- `transition_token`
- `label`

Optional:

- `run_id`

The authoring helper fills stable `run_id` values when they are omitted.

## Label balance

For local model-sequence checks, the helper requires:

- at least four records,
- at least two labels,
- at least two records per label,
- unique `run_id` values.

## Build default symbolic metadata input

```powershell
cd C:\Users\junny\Desktop\traceLeak\TraceLeak
traceleak-build-metadata-symbolic-input --out reports/local/openssl_metadata_demo/symbolic-metadata-input.json
```

## Adapt authored metadata into model-sequence shape

Create or reuse a runtime transition gate, then run the existing adapter:

```powershell
traceleak-validate-openssl-runtime-transition-gate --out reports/local/openssl_metadata_demo/runtime-gate.json --reviewer reviewer --reviewed-at 2026-06-14T00:00:00Z
traceleak-adapt-openssl-derived-metadata --metadata reports/local/openssl_metadata_demo/symbolic-metadata-input.json --runtime-gate reports/local/openssl_metadata_demo/runtime-gate.json --out reports/local/openssl_metadata_demo/symbolic-model-sequence.json
```

## Run authored symbolic metadata demo chain

This one-command path builds default symbolic metadata, adapts it into model-sequence shape, runs baseline and NN smoke checks, and writes a compact Markdown report.

```powershell
traceleak-run-symbolic-metadata-demo-chain --out-dir reports/local/symbolic_metadata_demo --epochs 20 --write-report
```

Generated local files should stay under `reports/local/`.
