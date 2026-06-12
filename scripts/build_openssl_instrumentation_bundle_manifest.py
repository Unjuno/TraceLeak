#!/usr/bin/env python3
"""Build a deterministic manifest for an OpenSSL instrumentation dry-run bundle."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from traceleak.openssl_instrumentation_bundle_manifest import (
    OpenSSLInstrumentationBundleManifestError,
    build_openssl_instrumentation_bundle_manifest,
    write_openssl_instrumentation_bundle_manifest_json,
    write_openssl_instrumentation_bundle_manifest_markdown,
)
from traceleak.openssl_trace_contract import OpenSSLTraceContractError, load_openssl_trace_contract


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build an OpenSSL instrumentation bundle manifest.")
    parser.add_argument("--contract", required=True, type=Path, help="OpenSSL trace contract JSON")
    parser.add_argument("--bundle-dir", required=True, type=Path, help="Instrumentation chain output directory")
    parser.add_argument("--out", required=True, type=Path, help="Manifest output path")
    parser.add_argument("--format", choices=["md", "json"], default="json", help="Manifest output format")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        contract = load_openssl_trace_contract(args.contract)
        manifest = build_openssl_instrumentation_bundle_manifest(
            contract=contract,
            bundle_dir=args.bundle_dir,
        )
        if args.format == "json":
            write_openssl_instrumentation_bundle_manifest_json(args.out, manifest)
        else:
            write_openssl_instrumentation_bundle_manifest_markdown(args.out, manifest)
    except (OpenSSLInstrumentationBundleManifestError, OpenSSLTraceContractError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(f"wrote OpenSSL instrumentation bundle manifest: {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
