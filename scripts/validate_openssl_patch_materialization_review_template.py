#!/usr/bin/env python3
"""Validate a saved pending OpenSSL patch-materialization review template."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from traceleak.openssl_patch_materialization_approval_template import (
    OpenSSLPatchMaterializationApprovalTemplateError,
    validate_openssl_patch_materialization_approval_template,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate a saved pending OpenSSL patch-materialization review template."
    )
    parser.add_argument("--template", required=True, type=Path, help="Review template JSON")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        value = json.loads(args.template.read_text(encoding="utf-8"))
        if not isinstance(value, dict):
            raise OpenSSLPatchMaterializationApprovalTemplateError(
                "review template must be a JSON object"
            )
        validate_openssl_patch_materialization_approval_template(value)
    except FileNotFoundError:
        print(f"error: review template not found: {args.template}", file=sys.stderr)
        return 1
    except json.JSONDecodeError as exc:
        print(f"error: invalid JSON in {args.template}: {exc}", file=sys.stderr)
        return 1
    except OpenSSLPatchMaterializationApprovalTemplateError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(f"valid OpenSSL patch materialization review template: {args.template}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
