# OpenSSL metadata demo fixtures

This directory contains small public-safe fixtures for the OpenSSL metadata demo path.

The checked-in JSON fixture is symbolic metadata only. It contains no OpenSSL source text, command text, build output, execution output, raw capture, runtime payload, or raw values.

The full demo artifact set can be generated locally with:

```powershell
traceleak-run-openssl-metadata-demo-chain --out-dir reports/local/openssl_metadata_demo --record-count 4 --epochs 20
```

Generated files are intended to live under `reports/local/` rather than being committed by default.
