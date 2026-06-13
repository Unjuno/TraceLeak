import json

from scripts import build_openssl_isolated_execution_plan as cli
from traceleak.openssl_isolated_execution_plan import PLANNED_EXECUTION_STEPS


def test_build_openssl_isolated_execution_plan_cli_writes_plan(tmp_path, monkeypatch) -> None:
    out = tmp_path / "plan.json"
    monkeypatch.setattr(
        "sys.argv",
        [
            "build_openssl_isolated_execution_plan",
            "--out",
            str(out),
            "--source-pin-digest",
            "sha256:source-pin",
            "--trace-contract-digest",
            "sha256:trace-contract",
            "--workspace-root",
            "C:/tmp/traceleak-openssl-workspace",
            "--cleanup-plan",
            "remove isolated workspace after review",
        ],
    )

    assert cli.main() == 0

    plan = json.loads(out.read_text(encoding="utf-8"))
    assert plan["format"] == "traceleak.openssl_isolated_execution_plan.v1"
    assert plan["status"] == "planned_not_executable"
    assert plan["mode"] == "plan_only"
    assert [step["name"] for step in plan["steps"]] == PLANNED_EXECUTION_STEPS
    assert {step["command_materialized"] for step in plan["steps"]} == {False}
    assert {step["result_captured"] for step in plan["steps"]} == {False}
    assert plan["execution_allowed"] is False
    assert plan["compile_allowed"] is False
    assert plan["patch_application_allowed"] is False
    assert plan["raw_capture_allowed"] is False
