import json
from pathlib import Path

import pytest

from pr_pathfinder.baseline import BASELINE_VERSION, load_baseline, write_baseline
from pr_pathfinder.cli import main
from pr_pathfinder.scanner import scan_repository

FIXTURES = Path(__file__).parent / "fixtures"


def _write_readme(directory: Path) -> None:
    (directory / "README.md").write_text("# Fixture\n", encoding="utf-8")


def test_baseline_suppresses_known_findings(tmp_path: Path) -> None:
    _write_readme(tmp_path)
    baseline = tmp_path / "baseline.json"
    write_baseline(baseline, scan_repository(tmp_path).findings)

    result = scan_repository(tmp_path, baseline=load_baseline(baseline))

    assert result.findings == ()


def test_baseline_reports_only_new_findings(tmp_path: Path) -> None:
    _write_readme(tmp_path)
    baseline = tmp_path / "baseline.json"
    write_baseline(baseline, scan_repository(tmp_path).findings)
    (tmp_path / "CONTRIBUTING.md").write_text(
        "# Contributing\n\nRun the tests before opening a pull request.\n",
        encoding="utf-8",
    )

    result = scan_repository(tmp_path, baseline=load_baseline(baseline))
    rule_ids = {finding.rule_id for finding in result.findings}

    assert "community/license" not in rule_ids
    assert "community/runnable-commands" in rule_ids


def test_stale_baseline_entries_are_ignored(tmp_path: Path) -> None:
    _write_readme(tmp_path)
    baseline = tmp_path / "baseline.json"
    write_baseline(baseline, scan_repository(tmp_path).findings)
    document = json.loads(baseline.read_text(encoding="utf-8"))
    document["findings"].append("stale/rule|nowhere|Stale entry")
    baseline.write_text(json.dumps(document), encoding="utf-8")

    result = scan_repository(tmp_path, baseline=load_baseline(baseline))

    assert result.findings == ()


def test_missing_baseline_file_points_to_write_flag(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="write-baseline"):
        load_baseline(tmp_path / "does-not-exist.json")


def test_malformed_baseline_is_rejected(tmp_path: Path) -> None:
    baseline = tmp_path / "baseline.json"
    baseline.write_text("{oops", encoding="utf-8")

    with pytest.raises(ValueError, match="Invalid baseline file"):
        load_baseline(baseline)


def test_wrong_baseline_version_is_rejected(tmp_path: Path) -> None:
    baseline = tmp_path / "baseline.json"
    baseline.write_text(
        json.dumps({"version": BASELINE_VERSION + 1, "findings": []}), encoding="utf-8"
    )

    with pytest.raises(ValueError, match="expected version"):
        load_baseline(baseline)


def test_cli_write_and_read_baseline(tmp_path: Path, capsys) -> None:
    _write_readme(tmp_path)
    baseline = tmp_path / "baseline.json"

    assert main(["check", str(tmp_path), "--write-baseline", str(baseline)]) == 0
    assert baseline.is_file()

    exit_code = main(
        [
            "check",
            str(tmp_path),
            "--format",
            "json",
            "--fail-on",
            "none",
            "--baseline",
            str(baseline),
        ]
    )
    payload = json.loads(capsys.readouterr().out)
    assert exit_code == 0
    assert payload["findings"] == []
