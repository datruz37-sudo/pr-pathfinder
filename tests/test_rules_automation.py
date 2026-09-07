from pathlib import Path

from pr_pathfinder.models import RuleContext
from pr_pathfinder.rules.automation import RULES


def _rule(rule_id: str):
    return next(item for item in RULES if item.rule_id == rule_id)


def _write(tmp_path: Path, relative: str, content: str = "# placeholder\n") -> None:
    target = tmp_path / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")


def test_bug_template_with_dashes_is_recognized(tmp_path: Path) -> None:
    _write(tmp_path, ".github/ISSUE_TEMPLATE/bug-report.yml")

    assert _rule("automation/issue-template").check(RuleContext(root=tmp_path)) == []


def test_missing_file_lists_searched_locations(tmp_path: Path) -> None:
    findings = _rule("automation/issue-template").check(RuleContext(root=tmp_path))

    assert len(findings) == 1
    assert ".github/ISSUE_TEMPLATE/bug.yml" in findings[0].detail
    assert ".github/ISSUE_TEMPLATE/bug-report.yml" in findings[0].detail
