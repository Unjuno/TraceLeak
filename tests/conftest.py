import pytest

from traceleak.openssl_metadata_demo_chain import build_openssl_metadata_demo_chain
from traceleak.openssl_runtime_transition_gate import build_openssl_runtime_transition_gate


@pytest.fixture
def metadata_demo_artifacts() -> dict:
    return build_openssl_metadata_demo_chain(epochs=20)


@pytest.fixture
def runtime_transition_gate() -> dict:
    return build_openssl_runtime_transition_gate(
        reviewer="reviewer",
        reviewed_at="2026-06-14T00:00:00Z",
    )
