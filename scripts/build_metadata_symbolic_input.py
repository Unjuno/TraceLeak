#!/usr/bin/env python3
"""Build a default metadata-only symbolic input JSON."""

from __future__ import annotations

import argparse
from pathlib import Path

from traceleak.metadata_symbolic_authoring import (
    build_symbolic_metadata_input,
    write_symbolic_metadata_input,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a metadata-only symbolic input JSON.")
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--source-pin-digest", default="sha256:source-pin")
    parser.add_argument("--label-name", default="metadata_bucket")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        payload = build_symbolic_metadata_input(
            records=_default_records(),
            source_pin_digest=args.source_pin_digest,
            label_name=args.label_name,
        )
        write_symbolic_metadata_input(args.out, payload)
    except Exception as exc:
        print(f"invalid symbolic metadata authoring request: {exc}")
        return 1
    print(f"wrote symbolic metadata input: {args.out}")
    return 0


def _default_records() -> list[dict[str, str]]:
    return [
        {
            "source_region_token": "ct_helper_family_a",
            "transition_token": "branch_symbolic_a",
            "label": "bucket_a",
        },
        {
            "source_region_token": "ct_helper_family_a2",
            "transition_token": "branch_symbolic_a2",
            "label": "bucket_a",
        },
        {
            "source_region_token": "ct_helper_family_b",
            "transition_token": "branch_symbolic_b",
            "label": "bucket_b",
        },
        {
            "source_region_token": "ct_helper_family_b2",
            "transition_token": "branch_symbolic_b2",
            "label": "bucket_b",
        },
    ]


if __name__ == "__main__":
    raise SystemExit(main())
