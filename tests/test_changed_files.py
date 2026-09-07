import json
from dataclasses import dataclass
from pathlib import Path

import pytest

from pr_pathfinder.cli import main
from pr_pathfinder.models import Finding, RuleContext, Severity
from pr_pathfinder.scanner import load_changed_files, scan_repository

FIXTURES = Path(__file__).parent / "fixtures"


@dataclass(frozen=True)
class _FloatingRule:
    rule_id: str = "test/floating"
    summary: str = "stub rule without a location"

    def check(self, context: RuleContext) -> list[Finding]:
        return [
            Finding(
                rule_id=self.rule_id,
                severity=Severity.WARNING,
                title="Floating stub finding",
                detail="Cannot be attributed to a file.",
                recommendation="Ignore this stub.",
                path=None,
            )
        ]


def test_only_listed_paths_are_reported() -> None:
    result = scan_repository(FIXTURES / "minimal", changed_files={"README.md"})

    assert result.findings == ()


def test_unlisted_paths_are_hidden() -> None:
    full = scan_repository(FIXTURES / "minimal")
    assert "community/license" in {finding.rule_id for finding in full.findings}

    filtered = scan_repository(FIXTURES / "minimal", changed_files={"README.md"})

    assert "community/license" not in {finding.rule_id for finding in filtered.findings}


def test_directory_entry_matches_nested_paths() -> None:
    result = scan_repository(FIXTURES / "minimal", changed_files={".github"})
    rule_ids = {finding.rule_id for finding in result.findings}

    assert "automation/continuous-integration" in rule_ids
    assert "community/license" not in rule_ids


def test_finding_without_path_is_always_shown(tmp_path: Path) -> None:
    result = scan_repository(tmp_path, rules=[_FloatingRule()], changed_files={"unrelated.md"})

    assert [finding.rule_id for finding in result.findings] == ["test/floating"]


def test_backslash_entries_match(tmp_path: Path) -> None:
    listed = load_changed_files(_write_list(tmp_path, "docs\\guide.md\n"))

    assert "docs/guide.md" in listed


def test_bom_comments_and_blank_lines_are_ignored(tmp_path: Path) -> None:
    listing = tmp_path / "changed.txt"
    listing.write_bytes(b"\xef\xbb\xbfREADME.md\n# only the readme\n\n")

    assert load_changed_files(listing) == {"README.md"}


def _write_list(tmp_path: Path, content: str) -> Path:
    listing = tmp_path / "changed.txt"
    listing.write_text(content, encoding="utf-8")
    return listing


def test_missing_list_file_is_rejected(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="Changed-files list not found"):
        load_changed_files(tmp_path / "does-not-exist.txt")


def test_cli_changed_files_filters_json(tmp_path: Path, capsys) -> None:
    import shutil

    target = tmp_path / "repo"
    shutil.copytree(FIXTURES / "minimal", target)
    listing = _write_list(tmp_path, "# only the readme\nREADME.md\n\n")

    exit_code = main(
        [
            "check",
            str(target),
            "--format",
            "json",
            "--fail-on",
            "none",
            "--changed-files",
            str(listing),
        ]
    )

    payload = json.loads(capsys.readouterr().out)
    assert exit_code == 0
    assert payload["findings"] == []
