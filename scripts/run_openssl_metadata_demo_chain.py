#!/usr/bin/env python3
"""Run the public-safe OpenSSL metadata demo chain."""

from __future__ import annotations

import argparse
from pathlib import Path

from traceleak.metadata_demo_artifact_index import (
    build_metadata_demo_artifact_index,
    render_metadata_demo_artifact_index_markdown,
    write_metadata_demo_artifact_index_json,
    write_metadata_demo_artifact_index_markdown,
)
from traceleak.metadata_demo_markdown_summary import (
    render_metadata_demo_markdown_summary_from_artifacts,
    write_metadata_demo_markdown_summary,
)
from traceleak.metadata_demo_metrics import (
    build_metadata_demo_metrics_from_artifacts,
    write_metadata_demo_metrics_csv,
    write_metadata_demo_metrics_json,
)
from traceleak.openssl_metadata_demo_chain import (
    build_openssl_metadata_demo_chain,
    write_openssl_metadata_demo_chain,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the OpenSSL metadata-only public demo chain.")
    parser.add_argument("--out-dir", default=Path("reports/local/openssl_metadata_demo"), type=Path)
    parser.add_argument("--record-count", default=4, type=int)
    parser.add_argument("--epochs", default=20, type=int)
    parser.add_argument("--write-markdown-summary", action="store_true")
    parser.add_argument("--include-ranking", action="store_true")
    parser.add_argument("--write-metrics-json", action="store_true")
    parser.add_argument("--write-metrics-csv", action="store_true")
    parser.add_argument("--write-artifact-index-json", action="store_true")
    parser.add_argument("--write-artifact-index-markdown", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        artifacts = build_openssl_metadata_demo_chain(
            record_count=args.record_count,
            epochs=args.epochs,
        )
        paths = write_openssl_metadata_demo_chain(
            output_dir=args.out_dir,
            artifacts=artifacts,
        )
        if args.write_markdown_summary:
            markdown = render_metadata_demo_markdown_summary_from_artifacts(
                artifacts,
                include_ranking=args.include_ranking,
            )
            write_metadata_demo_markdown_summary(args.out_dir / "demo-summary.md", markdown)
        if args.write_metrics_json or args.write_metrics_csv:
            metrics = build_metadata_demo_metrics_from_artifacts(artifacts)
            if args.write_metrics_json:
                write_metadata_demo_metrics_json(args.out_dir / "demo-metrics.json", metrics)
            if args.write_metrics_csv:
                write_metadata_demo_metrics_csv(args.out_dir / "demo-metrics.csv", metrics)
        if args.write_artifact_index_json or args.write_artifact_index_markdown:
            index = build_metadata_demo_artifact_index(output_dir=args.out_dir)
            if args.write_artifact_index_json:
                write_metadata_demo_artifact_index_json(args.out_dir / "artifact-index.json", index)
            if args.write_artifact_index_markdown:
                write_metadata_demo_artifact_index_markdown(
                    args.out_dir / "artifact-index.md",
                    render_metadata_demo_artifact_index_markdown(index),
                )
    except Exception as exc:
        print(f"invalid OpenSSL metadata demo chain request: {exc}")
        return 1
    print(f"wrote OpenSSL metadata demo chain artifacts: {args.out_dir} ({len(paths)} file(s))")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
