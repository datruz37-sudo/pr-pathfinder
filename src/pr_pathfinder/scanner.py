"""Repository scanning orchestration."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import replace
from pathlib import Path

from pr_pathfinder.config import load_config
from pr_pathfinder.models import Finding, Rule, RuleContext, ScanResult
from pr_pathfinder.rules import builtin_rules


def normalize_repo_path(value: str) -> str:
    """Normalize a repo-relative path for comparison across platforms."""

    normalized = value.replace("\\", "/")
    while normalized.startswith("./"):
        normalized = normalized[2:]
    return normalized


def load_changed_files(path: Path) -> frozenset[str]:
    """Read a list of repo-relative paths (one per line, `#` comments allowed)."""

    try:
        lines = path.read_text(encoding="utf-8-sig").splitlines()
    except FileNotFoundError as exc:
        raise ValueError(
            f"Changed-files list not found: {path}. Generate it with `git diff --name-only`."
        ) from exc
    except OSError as exc:
        raise ValueError(f"Cannot read changed-files list {path}: {exc}") from exc
    return frozenset(
        normalize_repo_path(line.strip())
        for line in lines
        if line.strip() and not line.strip().startswith("#")
    )


def _touches(path: str | None, touched: frozenset[str]) -> bool:
    """A finding without a path cannot be attributed, so it is always shown."""

    if not path:
        return True
    normalized = normalize_repo_path(path)
    return any(normalized == entry or normalized.startswith(entry + "/") for entry in touched)


def scan_repository(
    root: Path,
    rules: Iterable[Rule] | None = None,
    ignore: Iterable[str] | None = None,
    baseline: Iterable[str] | None = None,
    changed_files: Iterable[str] | None = None,
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
    if baseline is not None:
        known = frozenset(baseline)
        findings = [item for item in findings if item.fingerprint() not in known]
    if changed_files is not None:
        touched = frozenset(normalize_repo_path(entry) for entry in changed_files)
        findings = [item for item in findings if _touches(item.path, touched)]
    return ScanResult(
        root=resolved_root,
        rules_run=len(selected_rules),
        findings=tuple(findings),
    )
