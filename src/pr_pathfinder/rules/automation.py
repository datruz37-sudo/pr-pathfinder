"""Rules for repository automation and review ergonomics."""

from __future__ import annotations

from pathlib import Path

from pr_pathfinder.models import Finding, Rule, RuleContext, Severity
from pr_pathfinder.rules.base import RequiredFileRule


class WorkflowPresenceRule:
    rule_id = "automation/continuous-integration"
    summary = "Repository runs automated checks for pull requests"

    def check(self, context: RuleContext) -> list[Finding]:
        workflow_dir = context.root / ".github" / "workflows"
        workflows = list(workflow_dir.glob("*.yml")) + list(workflow_dir.glob("*.yaml"))
        if any(self._looks_like_ci(path) for path in workflows):
            return []
        return [
            Finding(
                rule_id=self.rule_id,
                severity=Severity.WARNING,
                title="No pull-request CI workflow detected",
                detail="A first-time contributor cannot get automated feedback on a patch.",
                recommendation="Add a pull_request workflow that runs the documented checks.",
                path=".github/workflows/",
            )
        ]

    @staticmethod
    def _looks_like_ci(path: Path) -> bool:
        content = path.read_text(encoding="utf-8", errors="replace").lower()
        return "pull_request" in content and any(
            marker in content for marker in ("test", "check", "lint", "build")
        )


RULES: tuple[Rule, ...] = (
    RequiredFileRule(
        rule_id="automation/pull-request-template",
        summary="Repository includes a pull request template",
        paths=(
            ".github/pull_request_template.md",
            "pull_request_template.md",
            "docs/pull_request_template.md",
        ),
        title="Pull request template is missing",
        detail="Contributors receive no prompt for context, validation, or linked issues.",
        recommendation="Add a concise pull request template focused on reviewer needs.",
        severity=Severity.INFO,
    ),
    RequiredFileRule(
        rule_id="automation/issue-template",
        summary="Repository includes a structured issue template",
        paths=(
            ".github/ISSUE_TEMPLATE/bug.yml",
            ".github/ISSUE_TEMPLATE/bug_report.yml",
            ".github/ISSUE_TEMPLATE/bug_report.md",
            ".github/ISSUE_TEMPLATE/bug-report.yml",
            ".github/ISSUE_TEMPLATE/bug-report.md",
        ),
        title="Bug report template is missing",
        detail="Bug reports may omit reproduction steps and environment details.",
        recommendation="Add a GitHub issue form for reproducible bug reports.",
        severity=Severity.INFO,
    ),
    WorkflowPresenceRule(),
)
