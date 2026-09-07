from pathlib import Path

from pr_pathfinder.models import RuleContext
from pr_pathfinder.rules.base import RequiredFileRule
from pr_pathfinder.rules.community import RULES, RunnableCommandsRule

FIXTURES = Path(__file__).parent / "fixtures"


def _rule(rule_id: str):
    return next(item for item in RULES if item.rule_id == rule_id)


def test_changelog_rule_fires_when_no_history_file_exists() -> None:
    rule = _rule("community/changelog")
    assert isinstance(rule, RequiredFileRule)

    findings = rule.check(RuleContext(root=FIXTURES / "minimal"))

    assert [finding.rule_id for finding in findings] == ["community/changelog"]
    assert findings[0].path == "CHANGELOG.md"


def test_changelog_rule_passes_when_changelog_exists() -> None:
    assert _rule("community/changelog").check(RuleContext(root=FIXTURES / "healthy")) == []


def test_runnable_commands_rule_fires_on_prose_only_guide(tmp_path: Path) -> None:
    (tmp_path / "CONTRIBUTING.md").write_text(
        "# Contributing\n\n## Tests\n\nRun the tests before opening a pull request.\n",
        encoding="utf-8",
    )

    findings = RunnableCommandsRule().check(RuleContext(root=tmp_path))

    assert [finding.rule_id for finding in findings] == ["community/runnable-commands"]
    assert findings[0].path == "CONTRIBUTING.md"


def test_runnable_commands_rule_accepts_fenced_block(tmp_path: Path) -> None:
    (tmp_path / "CONTRIBUTING.md").write_text(
        "# Contributing\n\n## Tests\n\n```sh\npytest\n```\n",
        encoding="utf-8",
    )

    assert RunnableCommandsRule().check(RuleContext(root=tmp_path)) == []


def test_runnable_commands_rule_accepts_inline_code(tmp_path: Path) -> None:
    (tmp_path / "CONTRIBUTING.md").write_text(
        "# Contributing\n\n## Tests\n\nRun `pytest` before opening a pull request.\n",
        encoding="utf-8",
    )

    assert RunnableCommandsRule().check(RuleContext(root=tmp_path)) == []


def test_runnable_commands_rule_skips_repository_without_guide(tmp_path: Path) -> None:
    (tmp_path / "README.md").write_text("# Project\n", encoding="utf-8")

    assert RunnableCommandsRule().check(RuleContext(root=tmp_path)) == []
