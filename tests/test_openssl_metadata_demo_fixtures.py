import json
from pathlib import Path

from traceleak.openssl_derived_metadata_adapter import validate_openssl_derived_metadata_input


def test_symbolic_metadata_fixture_is_valid() -> None:
    path = Path("examples/openssl_metadata_demo/symbolic_metadata_input.json")
    payload = json.loads(path.read_text(encoding="utf-8"))

    validate_openssl_derived_metadata_input(payload)
    assert payload["metadata_only"] is True
    assert payload["payload_free"] is True
    assert payload["target_decision"] == "constant_time_helper_misuse_path"
