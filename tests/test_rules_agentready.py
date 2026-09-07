from pathlib import Path

from pr_pathfinder.models import RuleContext
from pr_pathfinder.rules.agentready import (
    ContextBudgetRule,
    DocumentedMakeTargetsRule,
)
from pr_pathfinder.rules.base import RequiredFileRule
from pr_pathfinder.scanner import scan_repository

FIXTURES = Path(__file__).parent / "fixtures"


def _instructions_rule() -> RequiredFileRule:
    from pr_pathfinder.rules.agentready import RULES

    rule = next(item for item in RULES if item.rule_id == "agentready/instructions")
    assert isinstance(rule, RequiredFileRule)
    return rule


def test_instructions_rule_fires_when_no_agent_file_exists() -> None:
    context = RuleContext(root=FIXTURES / "minimal")

    findings = _instructions_rule().check(context)

    assert [finding.rule_id for finding in findings] == ["agentready/instructions"]
    assert findings[0].path == "AGENTS.md"


def test_instructions_rule_passes_when_agents_md_exists() -> None:
    context = RuleContext(root=FIXTURES / "healthy")

    assert _instructions_rule().check(context) == []


def test_context_budget_flags_oversized_text_file(tmp_path: Path) -> None:
    (tmp_path / "huge.md").write_text("x" * 200_001, encoding="utf-8")

    findings = ContextBudgetRule().check(RuleContext(root=tmp_path))

    assert [finding.rule_id for finding in findings] == ["agentready/context-budget"]
    assert findings[0].path == "huge.md"
    assert "200,001 bytes" in findings[0].detail


def test_context_budget_ignores_small_and_binary_files(tmp_path: Path) -> None:
    (tmp_path / "small.md").write_text("x" * 100, encoding="utf-8")
    (tmp_path / "logo.png").write_bytes(b"\x89PNG" * 60_000)

    assert ContextBudgetRule().check(RuleContext(root=tmp_path)) == []


def test_context_budget_skips_vendored_directories(tmp_path: Path) -> None:
    (tmp_path / "node_modules").mkdir()
    (tmp_path / "node_modules" / "bundled.js").write_text("x" * 300_000, encoding="utf-8")

    assert ContextBudgetRule().check(RuleContext(root=tmp_path)) == []


def test_make_targets_require_a_makefile(tmp_path: Path) -> None:
    (tmp_path / "README.md").write_text("Run `make test` before opening a PR.", encoding="utf-8")

    findings = DocumentedMakeTargetsRule().check(RuleContext(root=tmp_path))

    assert [finding.rule_id for finding in findings] == ["agentready/documented-make-targets"]
    assert findings[0].path == "README.md"


def test_make_targets_pass_when_makefile_present(tmp_path: Path) -> None:
    (tmp_path / "README.md").write_text("Run `make test` before opening a PR.", encoding="utf-8")
    (tmp_path / "Makefile").write_text("test:\n\tpytest\n", encoding="utf-8")

    assert DocumentedMakeTargetsRule().check(RuleContext(root=tmp_path)) == []


def test_make_targets_pass_when_make_is_never_mentioned(tmp_path: Path) -> None:
    (tmp_path / "README.md").write_text("Run pytest before opening a PR.", encoding="utf-8")

    assert DocumentedMakeTargetsRule().check(RuleContext(root=tmp_path)) == []


def test_make_targets_ignore_prose_that_merely_contains_make(tmp_path: Path) -> None:
    (tmp_path / "CONTRIBUTING.md").write_text(
        "Thank you for helping make open source easier to enter.",
        encoding="utf-8",
    )

    assert DocumentedMakeTargetsRule().check(RuleContext(root=tmp_path)) == []


def test_make_targets_are_found_inside_fenced_blocks(tmp_path: Path) -> None:
    (tmp_path / "README.md").write_text(
        "## Build\n\n```sh\nmake build\n```\n",
        encoding="utf-8",
    )

    findings = DocumentedMakeTargetsRule().check(RuleContext(root=tmp_path))

    assert [finding.rule_id for finding in findings] == ["agentready/documented-make-targets"]


def test_healthy_fixture_still_scores_full_marks() -> None:
    result = scan_repository(FIXTURES / "healthy")

    assert result.findings == ()
    assert result.score == 100
