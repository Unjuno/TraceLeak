from examples.synthetic.target import bucket_loop_count, make_run
from traceleak.schema import validate_run


def test_bucket_loop_count() -> None:
    assert bucket_loop_count(64) == "064-079"
    assert bucket_loop_count(80) == "080-095"
    assert bucket_loop_count(96) == "096-111"
    assert bucket_loop_count(112) == "112-127"


def test_make_run_generates_valid_public_run() -> None:
    run = make_run(1, leak=True)
    validate_run(run, public_export=True)
    assert run["run_id"] == "synthetic_000001"
    assert run["view"] == "redacted"
    assert run["labels_lab_only"] == {"synthetic_bucket": 1}


def test_make_run_control_has_control_target() -> None:
    run = make_run(2, leak=False)
    validate_run(run, public_export=True)
    assert run["target"] == "synthetic-control"
