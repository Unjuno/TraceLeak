#!/usr/bin/env python3
"""Extract a pending OpenSSL patch-materialization approval skeleton."""

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
        description="Extract approval_record_skeleton from a pending OpenSSL review template."
    )
    parser.add_argument("--template", required=True, type=Path, help="Pending review template JSON")
    parser.add_argument("--out", required=True, type=Path, help="Output skeleton JSON")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        template = json.loads(args.template.read_text(encoding="utf-8"))
        if not isinstance(template, dict):
            raise OpenSSLPatchMaterializationApprovalTemplateError(
                "review template must be a JSON object"
            )
        validate_openssl_patch_materialization_approval_template(template)
        skeleton = template["approval_record_skeleton"]
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(skeleton, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    except FileNotFoundError:
        print(f"error: review template not found: {args.template}", file=sys.stderr)
        return 1
    except json.JSONDecodeError as exc:
        print(f"error: invalid JSON in {args.template}: {exc}", file=sys.stderr)
        return 1
    except OpenSSLPatchMaterializationApprovalTemplateError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(f"wrote OpenSSL approval skeleton: {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
