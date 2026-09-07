"""Repository scanning orchestration."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import replace
from pathlib import Path

from pr_pathfinder.config import load_config
from pr_pathfinder.models import Finding, Rule, RuleContext, ScanResult
from pr_pathfinder.rules import builtin_rules


def scan_repository(
    root: Path,
    rules: Iterable[Rule] | None = None,
    ignore: Iterable[str] | None = None,
) -> ScanResult:
    """Run rules against a local repository without modifying it."""

    resolved_root = root.expanduser().resolve()
    if not resolved_root.is_dir():
        raise NotADirectoryError(f"Repository path is not a directory: {resolved_root}")

    config = load_config(resolved_root)
    if ignore is None:
        ignore = config.ignore
    ignored = frozenset(ignore)
    included = None if config.include is None else frozenset(config.include)
    severity_overrides = dict(config.severity_overrides)
    selected_rules = tuple(
        rule
        for rule in (rules if rules is not None else builtin_rules())
        if (included is None or rule.rule_id in included) and rule.rule_id not in ignored
    )
    context = RuleContext(root=resolved_root)
    findings: list[Finding] = []
    for rule in selected_rules:
        for finding in rule.check(context):
            severity = severity_overrides.get(finding.rule_id)
            findings.append(
                replace(finding, severity=severity) if severity is not None else finding
            )

    findings.sort(key=lambda item: (-int(item.severity), item.rule_id, item.path or ""))
    return ScanResult(
        root=resolved_root,
        rules_run=len(selected_rules),
        findings=tuple(findings),
    )
