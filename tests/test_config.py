import json
from pathlib import Path
from shutil import copytree

import pytest

from pr_pathfinder.cli import main
from pr_pathfinder.config import Config, load_config
from pr_pathfinder.models import Severity
from pr_pathfinder.scanner import scan_repository

FIXTURES = Path(__file__).parent / "fixtures"


def test_missing_config_means_defaults() -> None:
    assert load_config(FIXTURES / "minimal") == Config()


def test_ignore_suppresses_only_listed_rules() -> None:
    # The ignore-config fixture mirrors minimal plus a config file.
    configured = scan_repository(FIXTURES / "ignore-config")
    plain = scan_repository(FIXTURES / "minimal")

    configured_ids = {finding.rule_id for finding in configured.findings}
    plain_ids = {finding.rule_id for finding in plain.findings}
    assert "community/license" in plain_ids
    assert configured_ids == plain_ids - {"community/license"}


def test_include_runs_only_selected_rules(tmp_path: Path) -> None:
    (tmp_path / "pr-pathfinder.toml").write_text(
        'include = ["community/license"]\n', encoding="utf-8"
    )

    result = scan_repository(tmp_path)

    assert result.rules_run == 1
    assert [finding.rule_id for finding in result.findings] == ["community/license"]


def test_ignore_wins_over_include(tmp_path: Path) -> None:
    (tmp_path / "pr-pathfinder.toml").write_text(
        'include = ["community/license"]\nignore = ["community/license"]\n', encoding="utf-8"
    )

    result = scan_repository(tmp_path)

    assert result.rules_run == 0
    assert result.findings == ()


def test_backwards_compatible_without_config() -> None:
    result = scan_repository(FIXTURES / "minimal")

    assert "community/license" in {finding.rule_id for finding in result.findings}


def test_unknown_ignore_id_warns_and_continues(tmp_path: Path) -> None:
    (tmp_path / "README.md").write_text("# Fixture\n", encoding="utf-8")
    (tmp_path / "pr-pathfinder.toml").write_text('ignore = ["nope/not-a-rule"]\n', encoding="utf-8")

    config = load_config(tmp_path)

    assert len(config.warnings) == 1
    assert "nope/not-a-rule" in config.warnings[0]
    result = scan_repository(tmp_path)
    assert result.findings


def test_unknown_include_rule_id_is_rejected(tmp_path: Path) -> None:
    (tmp_path / "pr-pathfinder.toml").write_text(
        'include = ["nope/not-a-rule"]\n', encoding="utf-8"
    )

    with pytest.raises(ValueError, match="unknown rule ids in 'include'"):
        load_config(tmp_path)


def test_malformed_toml_is_rejected(tmp_path: Path) -> None:
    (tmp_path / "pr-pathfinder.toml").write_text("ignore = [\n", encoding="utf-8")

    with pytest.raises(ValueError, match="Invalid pr-pathfinder.toml"):
        load_config(tmp_path)


def test_ignore_must_be_a_list_of_strings(tmp_path: Path) -> None:
    (tmp_path / "pr-pathfinder.toml").write_text('ignore = "community/license"\n', encoding="utf-8")

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


def test_severity_override_changes_finding_and_exit_status(tmp_path: Path) -> None:
    copytree(FIXTURES / "healthy", tmp_path, dirs_exist_ok=True)
    (tmp_path / "LICENSE").unlink()
    (tmp_path / "pr-pathfinder.toml").write_text(
        '[severity]\n"community/license" = "info"\n', encoding="utf-8"
    )

    result = scan_repository(tmp_path)

    license_finding = next(
        finding for finding in result.findings if finding.rule_id == "community/license"
    )
    assert license_finding.severity is Severity.INFO
    assert not result.should_fail(Severity.WARNING)


def test_severity_override_is_validated(tmp_path: Path) -> None:
    (tmp_path / "pr-pathfinder.toml").write_text(
        '[severity]\n"community/license" = "urgent"\n', encoding="utf-8"
    )

    with pytest.raises(ValueError, match="severity for 'community/license' must be one of"):
        load_config(tmp_path)


def test_severity_override_requires_known_rule(tmp_path: Path) -> None:
    (tmp_path / "pr-pathfinder.toml").write_text(
        '[severity]\n"unknown/rule" = "warning"\n', encoding="utf-8"
    )

    with pytest.raises(ValueError, match="unknown rule ids in 'severity': unknown/rule"):
        load_config(tmp_path)


def test_unknown_setting_is_validated(tmp_path: Path) -> None:
    (tmp_path / "pr-pathfinder.toml").write_text("ignroe = []\n", encoding="utf-8")

    with pytest.raises(ValueError, match="unknown settings: ignroe"):
        load_config(tmp_path)


def test_empty_include_is_rejected(tmp_path: Path) -> None:
    (tmp_path / "pr-pathfinder.toml").write_text("include = []\n", encoding="utf-8")

    with pytest.raises(ValueError, match="at least one rule"):
        load_config(tmp_path)


def test_json_report_carries_versioned_contract() -> None:
    from pr_pathfinder import __version__
    from pr_pathfinder.models import SCHEMA_VERSION

    payload = scan_repository(FIXTURES / "minimal").to_dict()

    assert payload["schema_version"] == SCHEMA_VERSION == 1
    assert payload["tool_version"] == __version__
    assert "root" not in payload


def test_cli_prints_config_warnings_to_stderr(tmp_path: Path, capsys) -> None:
    (tmp_path / "README.md").write_text("# Fixture\n", encoding="utf-8")
    (tmp_path / "pr-pathfinder.toml").write_text('ignore = ["nope/not-a-rule"]\n', encoding="utf-8")

    exit_code = main(["check", str(tmp_path), "--format", "json", "--fail-on", "none"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "nope/not-a-rule" in captured.err
    assert json.loads(captured.out)["findings"]
