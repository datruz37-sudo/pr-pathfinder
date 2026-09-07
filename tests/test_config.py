import json
from pathlib import Path

import pytest

from pr_pathfinder.cli import main
from pr_pathfinder.config import Config, load_config
from pr_pathfinder.scanner import scan_repository

FIXTURES = Path(__file__).parent / "fixtures"

EXPECTED_MINIMAL_RULES = {
    "community/license",
    "community/contributing",
    "automation/continuous-integration",
}


def test_missing_config_means_defaults() -> None:
    assert load_config(FIXTURES / "minimal") == Config(ignore=())


def test_ignore_suppresses_only_listed_rules() -> None:
    result = scan_repository(FIXTURES / "ignore-config")

    rule_ids = {finding.rule_id for finding in result.findings}
    assert "community/license" not in rule_ids
    assert rule_ids == EXPECTED_MINIMAL_RULES - {"community/license"}


def test_backwards_compatible_without_config() -> None:
    result = scan_repository(FIXTURES / "minimal")

    assert {finding.rule_id for finding in result.findings} == EXPECTED_MINIMAL_RULES


def test_unknown_rule_id_is_rejected(tmp_path: Path) -> None:
    (tmp_path / "pr-pathfinder.toml").write_text(
        'ignore = ["nope/not-a-rule"]\n', encoding="utf-8"
    )

    with pytest.raises(ValueError, match="unknown rule ids"):
        load_config(tmp_path)


def test_malformed_toml_is_rejected(tmp_path: Path) -> None:
    (tmp_path / "pr-pathfinder.toml").write_text("ignore = [\n", encoding="utf-8")

    with pytest.raises(ValueError, match="Invalid pr-pathfinder.toml"):
        load_config(tmp_path)


def test_ignore_must_be_a_list_of_strings(tmp_path: Path) -> None:
    (tmp_path / "pr-pathfinder.toml").write_text(
        'ignore = "community/license"\n', encoding="utf-8"
    )

    with pytest.raises(ValueError, match="'ignore' must be a list"):
        load_config(tmp_path)


def test_cli_honours_config_file(capsys) -> None:
    exit_code = main(
        ["check", str(FIXTURES / "ignore-config"), "--format", "json", "--fail-on", "none"]
    )

    payload = json.loads(capsys.readouterr().out)
    assert exit_code == 0
    rule_ids = {finding["rule_id"] for finding in payload["findings"]}
    assert "community/license" not in rule_ids
    assert rule_ids
