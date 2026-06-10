"""Toy RSA-like target for TraceLeak public-safe examples.

This is not an RSA implementation and provides no cryptographic security. It is
only a small key-generation-shaped process for validating TraceLeak's trace,
feature, baseline, and reporting workflow before any OpenSSL work.
"""

from __future__ import annotations

import argparse
import json
import random
from pathlib import Path
from typing import Any

SMALL_DIVISORS = (3, 5, 7, 11, 13)


def make_run(index: int) -> dict[str, Any]:
    """Create one public-safe toy RSA-like trace run."""

    rng = random.Random(10_000 + index)
    accept_after = 1 + (index % 4)
    last_reason = "none"
    accepted_bucket = "unreached"
    divisor_bucket = "none"

    for attempt in range(1, accept_after + 1):
        candidate = _make_candidate(rng, index, attempt, accept_after)
        if candidate % 2 == 0:
            last_reason = "even"
            divisor_bucket = "none"
            continue
        divisor = _first_small_divisor(candidate)
        if divisor is not None:
            last_reason = "small_divisor"
            divisor_bucket = _bucket_divisor(divisor)
            continue
        last_reason = "accepted"
        divisor_bucket = "none"
        accepted_bucket = _bucket_attempt(attempt)
        break

    return {
        "run_id": f"toy_rsa_like_{index:06d}",
        "target": "toy-rsa-like",
        "target_version": "v0",
        "view": "redacted",
        "events": [
            {
                "step": 1,
                "phase": "candidate_generation",
                "function": "toy_rsa_like_keygen",
                "file": "examples/toy_rsa_like/target.py",
                "line": 21,
                "event_type": "phase",
                "name": "candidate_generated",
                "value_redacted": {
                    "candidate_bit_length_bucket": _bucket_bit_length(candidate.bit_length()),
                    "attempt_bucket": _bucket_attempt(accept_after),
                },
            },
            {
                "step": 2,
                "phase": "candidate_filter",
                "function": "toy_rsa_like_keygen",
                "file": "examples/toy_rsa_like/target.py",
                "line": 25,
                "event_type": "branch",
                "name": "oddness_check",
                "value_redacted": {"is_odd": bool(candidate % 2)},
            },
            {
                "step": 3,
                "phase": "candidate_filter",
                "function": "toy_rsa_like_keygen",
                "file": "examples/toy_rsa_like/target.py",
                "line": 29,
                "event_type": "loop",
                "name": "small_divisor_check",
                "value_redacted": {
                    "small_divisor_bucket": divisor_bucket,
                    "small_divisor_count_bucket": _bucket_divisor_count(len(SMALL_DIVISORS)),
                },
            },
            {
                "step": 4,
                "phase": "candidate_result",
                "function": "toy_rsa_like_keygen",
                "file": "examples/toy_rsa_like/target.py",
                "line": 35,
                "event_type": "branch",
                "name": "candidate_result",
                "value_redacted": {
                    "result_bucket": last_reason,
                    "accepted_attempt_bucket": accepted_bucket,
                },
            },
        ],
        "labels_lab_only": {
            "toy_accept_attempt_bucket": accepted_bucket,
            "toy_result_bucket": last_reason,
        },
    }


def _make_candidate(rng: random.Random, index: int, attempt: int, accept_after: int) -> int:
    """Create a local-only toy candidate value.

    The raw value is never emitted in traces.
    """

    value = 2_000 + rng.randint(0, 2_000) + index * 17 + attempt * 31
    if attempt == accept_after:
        value |= 1
        while _first_small_divisor(value) is not None:
            value += 2
    elif attempt % 2 == 0:
        value |= 1
        value *= 3
    else:
        value &= ~1
    return value


def _first_small_divisor(value: int) -> int | None:
    for divisor in SMALL_DIVISORS:
        if value % divisor == 0:
            return divisor
    return None


def _bucket_bit_length(bit_length: int) -> str:
    if bit_length <= 11:
        return "000-011"
    if bit_length <= 12:
        return "012"
    return "013-plus"


def _bucket_attempt(attempt: int) -> str:
    if attempt <= 1:
        return "1"
    if attempt == 2:
        return "2"
    return "3-plus"


def _bucket_divisor(divisor: int) -> str:
    if divisor <= 5:
        return "small"
    if divisor <= 11:
        return "medium"
    return "large"


def _bucket_divisor_count(count: int) -> str:
    if count <= 3:
        return "0-3"
    if count <= 6:
        return "4-6"
    return "7-plus"


def write_jsonl(path: Path, runs: list[dict[str, Any]]) -> None:
    """Write runs as compact JSONL."""

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for run in runs:
            handle.write(json.dumps(run, sort_keys=True, separators=(",", ":")) + "\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate toy RSA-like TraceLeak traces.")
    parser.add_argument("--out", type=Path, required=True, help="Output JSONL path")
    parser.add_argument("--runs", type=int, default=16, help="Number of runs")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.runs <= 0:
        raise SystemExit("error: --runs must be positive")
    runs = [make_run(index) for index in range(args.runs)]
    write_jsonl(args.out, runs)
    print(f"wrote toy RSA-like traces: {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
