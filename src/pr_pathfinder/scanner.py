"""Repository scanning orchestration."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

from pr_pathfinder.models import Finding, Rule, RuleContext, ScanResult
from pr_pathfinder.rules import builtin_rules


def scan_repository(root: Path, rules: Iterable[Rule] | None = None) -> ScanResult:
    """Run rules against a local repository without modifying it."""

    resolved_root = root.expanduser().resolve()
    if not resolved_root.is_dir():
        raise NotADirectoryError(f"Repository path is not a directory: {resolved_root}")

    selected_rules = tuple(rules if rules is not None else builtin_rules())
    context = RuleContext(root=resolved_root)
    findings: list[Finding] = []
    for rule in selected_rules:
        findings.extend(rule.check(context))

    findings.sort(key=lambda item: (-int(item.severity), item.rule_id, item.path or ""))
    return ScanResult(
        root=resolved_root,
        rules_run=len(selected_rules),
        findings=tuple(findings),
    )
