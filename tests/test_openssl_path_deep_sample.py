from scripts.build_path_deep_sample import build_from_manifest
from traceleak.deep_program_dataset import DEEP_PROGRAM_DATASET_FORMAT
from traceleak.openssl_path_deep_sample import build_openssl_path_deep_program_sample


def test_build_openssl_path_deep_program_sample() -> None:
    sample = build_openssl_path_deep_program_sample(
        sample_id="openssl_path_sample_000001",
        path_records=[
            {"path": "crypto/bn/bn_lib.c", "role": "bignum"},
            {"path": "crypto/evp/digest.c", "role": "generic"},
            {"path": "ssl/statem/statem_lib.c", "role": "generic"},
        ],
    )
    assert sample["format"] == DEEP_PROGRAM_DATASET_FORMAT
    assert sample["metadata"]["path_record_count"] == 3
    assert sample["masks"]["use_program_events"] is True
    assert sample["masks"]["use_variable_state_sequence"] is True
    assert sample["masks"]["use_dependency_graph"] is True


def test_build_path_deep_sample_cli_builder_is_callable() -> None:
    assert callable(build_from_manifest)
