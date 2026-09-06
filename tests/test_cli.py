import json
from pathlib import Path

from pr_pathfinder.cli import main


FIXTURES = Path(__file__).parent / "fixtures"


def test_json_output_is_machine_readable(capsys) -> None:
    exit_code = main(
        ["check", str(FIXTURES / "minimal"), "--format", "json", "--fail-on", "none"]
    )

    payload = json.loads(capsys.readouterr().out)
    assert exit_code == 0
    assert payload["score"] < 100
    assert payload["findings"]


def test_fail_on_error_returns_one() -> None:
    assert main(["check", str(FIXTURES / "minimal"), "--fail-on", "error"]) == 1


def test_rules_lists_stable_identifiers(capsys) -> None:
    assert main(["rules"]) == 0
    output = capsys.readouterr().out
    assert "community/readme" in output
    assert "automation/continuous-integration" in output
