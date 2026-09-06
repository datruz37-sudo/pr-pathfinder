"""Human-readable and machine-readable report formats."""

from __future__ import annotations

import json

from pr_pathfinder.models import ScanResult

_SYMBOLS = {"error": "ERR", "warning": "WARN", "info": "INFO"}


def render_text(result: ScanResult) -> str:
    counts = result.counts
    lines = [
        f"pr-pathfinder: {result.root}",
        f"Score: {result.score}/100 | Rules: {result.rules_run} | "
        f"Errors: {counts['error']} | Warnings: {counts['warning']} | Info: {counts['info']}",
    ]
    if not result.findings:
        lines.append("No onboarding blockers found.")
        return "\n".join(lines)

    for finding in result.findings:
        severity = finding.severity.name.lower()
        location = f" ({finding.path})" if finding.path else ""
        lines.extend(
            [
                "",
                f"[{_SYMBOLS[severity]}] {finding.rule_id}{location}",
                f"  {finding.title}",
                f"  Why: {finding.detail}",
                f"  Fix: {finding.recommendation}",
            ]
        )
    return "\n".join(lines)


def render_json(result: ScanResult) -> str:
    return json.dumps(result.to_dict(), indent=2, sort_keys=True)


def render_markdown(result: ScanResult) -> str:
    counts = result.counts
    lines = [
        "# pr-pathfinder report",
        "",
        f"**Score:** {result.score}/100  ",
        f"**Rules run:** {result.rules_run}  ",
        f"**Findings:** {counts['error']} errors, {counts['warning']} warnings, "
        f"{counts['info']} informational",
        "",
    ]
    if not result.findings:
        lines.append("No onboarding blockers found.")
        return "\n".join(lines)

    lines.extend(
        [
            "| Severity | Rule | Location | Finding |",
            "| --- | --- | --- | --- |",
        ]
    )
    for finding in result.findings:
        location = finding.path or "—"
        title = finding.title.replace("|", "\\|")
        lines.append(
            f"| {finding.severity.name.lower()} | `{finding.rule_id}` | `{location}` | {title} |"
        )
    lines.extend(["", "## Recommendations", ""])
    for finding in result.findings:
        lines.append(f"- **{finding.rule_id}:** {finding.recommendation}")
    return "\n".join(lines)
