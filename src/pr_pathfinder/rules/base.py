"""Rule helpers that keep individual checks small and testable."""

from __future__ import annotations

from dataclasses import dataclass

from pr_pathfinder.models import Finding, RuleContext, Severity


@dataclass(frozen=True, slots=True)
class RequiredFileRule:
    """Require at least one path from a set of conventional locations."""

    rule_id: str
    summary: str
    paths: tuple[str, ...]
    title: str
    detail: str
    recommendation: str
    severity: Severity = Severity.ERROR

    def check(self, context: RuleContext) -> list[Finding]:
        if context.exists_any(*self.paths):
            return []
        searched = ", ".join(self.paths)
        return [
            Finding(
                rule_id=self.rule_id,
                severity=self.severity,
                title=self.title,
                detail=f"{self.detail} Looked in: {searched}.",
                recommendation=self.recommendation,
                path=self.paths[0],
            )
        ]
