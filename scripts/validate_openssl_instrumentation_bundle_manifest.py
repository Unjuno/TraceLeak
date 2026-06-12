#!/usr/bin/env python3
"""Validate a saved OpenSSL instrumentation dry-run bundle manifest."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from traceleak.openssl_instrumentation_bundle_manifest import (
    OpenSSLInstrumentationBundleManifestError,
    load_openssl_instrumentation_bundle_manifest,
    validate_openssl_instrumentation_bundle_manifest,
)
from traceleak.openssl_trace_contract import OpenSSLTraceContractError, load_openssl_trace_contract


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate an OpenSSL instrumentation bundle manifest.")
    parser.add_argument("--contract", required=True, type=Path, help="OpenSSL trace contract JSON")
    parser.add_argument("--bundle-dir", required=True, type=Path, help="Instrumentation chain output directory")
    parser.add_argument("--manifest", required=True, type=Path, help="Bundle manifest JSON")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        contract = load_openssl_trace_contract(args.contract)
        manifest = load_openssl_instrumentation_bundle_manifest(args.manifest)
        validate_openssl_instrumentation_bundle_manifest(
            contract=contract,
            bundle_dir=args.bundle_dir,
            manifest=manifest,
        )
    except (OpenSSLInstrumentationBundleManifestError, OpenSSLTraceContractError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(f"valid OpenSSL instrumentation bundle manifest: {args.manifest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
