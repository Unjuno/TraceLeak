import json

import pytest

from tests.test_level13_closure_manifest import checkpoint
from traceleak.level13_closure import (
    LEVEL13_HANDOFF_INVENTORY_FORMAT,
    Level13ClosureError,
    build_level13_closure_manifest,
    build_level13_handoff_inventory,
    validate_level13_handoff_inventory,
    write_level13_handoff_inventory,
)


def manifest():
    return build_level13_closure_manifest(review_checkpoint=checkpoint())


def test_handoff_inventory_default_families() -> None:
    inventory = build_level13_handoff_inventory(closure_manifest=manifest())

    assert inventory["format"] == LEVEL13_HANDOFF_INVENTORY_FORMAT
    assert inventory["phase"] == "P138"
    assert inventory["closure_status"] == "ready_for_handoff"
    assert len(inventory["families"]) >= 7
    assert inventory["flags"]["path_only"] is True
    assert inventory["flags"]["content_read"] is False
    assert inventory["flags"]["claim_generated"] is False
    validate_level13_handoff_inventory(inventory)


def test_handoff_inventory_rejects_unsafe_path() -> None:
    families = [
        {
            "family": "unsafe",
            "role": "unsafe family",
            "paths": ["../reports/local/unsafe.json"],
        }
    ]

    with pytest.raises(Level13ClosureError, match="relative"):
        build_level13_handoff_inventory(closure_manifest=manifest(), families=families)


def test_handoff_inventory_rejects_duplicate_family() -> None:
    families = [
        {
            "family": "dup",
            "role": "family a",
            "paths": ["reports/local/a.json"],
        },
        {
            "family": "dup",
            "role": "family b",
            "paths": ["reports/local/b.json"],
        },
    ]

    with pytest.raises(Level13ClosureError, match="unique"):
        build_level13_handoff_inventory(closure_manifest=manifest(), families=families)


def test_handoff_inventory_writer(tmp_path) -> None:
    inventory = build_level13_handoff_inventory(closure_manifest=manifest())
    path = tmp_path / "level13-handoff-inventory.json"

    write_level13_handoff_inventory(path, inventory)

    assert json.loads(path.read_text(encoding="utf-8"))["format"] == LEVEL13_HANDOFF_INVENTORY_FORMAT
