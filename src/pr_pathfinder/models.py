"""Shared data models for scans and reports."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import IntEnum
from pathlib import Path
from typing import Protocol


class Severity(IntEnum):
    """Finding severity ordered from least to most important."""

    INFO = 1
    WARNING = 2
    ERROR = 3

    @classmethod
    def parse(cls, value: str) -> Severity:
        try:
            return cls[value.upper()]
        except KeyError as exc:
            choices = ", ".join(item.name.lower() for item in cls)
            raise ValueError(f"Unknown severity {value!r}; choose one of: {choices}") from exc


@dataclass(frozen=True, slots=True)
class Finding:
    """A single, actionable observation produced by a rule."""

    rule_id: str
    severity: Severity
    title: str
    detail: str
    recommendation: str
    path: str | None = None

    def to_dict(self) -> dict[str, object]:
        data = asdict(self)
        data["severity"] = self.severity.name.lower()
        return data


@dataclass(frozen=True, slots=True)
class RuleContext:
    """Read-only view of the repository under inspection."""

    root: Path

    def exists_any(self, *relative_paths: str) -> bool:
        return any((self.root / path).exists() for path in relative_paths)

    def read_first(self, *relative_paths: str) -> tuple[str | None, str]:
        for relative_path in relative_paths:
            candidate = self.root / relative_path
            if candidate.is_file():
                return relative_path, candidate.read_text(encoding="utf-8", errors="replace")
        return None, ""


class Rule(Protocol):
    """Contract implemented by every onboarding rule."""

    rule_id: str
    summary: str

    def check(self, context: RuleContext) -> list[Finding]:
        """Return zero or more findings for the repository."""


@dataclass(frozen=True, slots=True)
class ScanResult:
    """Complete result of a repository scan."""

    root: Path
    rules_run: int
    findings: tuple[Finding, ...]

    @property
    def counts(self) -> dict[str, int]:
        return {
            severity.name.lower(): sum(item.severity is severity for item in self.findings)
            for severity in Severity
        }

    @property
    def score(self) -> int:
        penalties = sum(
            {Severity.INFO: 2, Severity.WARNING: 6, Severity.ERROR: 12}[item.severity]
            for item in self.findings
        )
        return max(0, 100 - penalties)

    def should_fail(self, threshold: Severity) -> bool:
        return any(item.severity >= threshold for item in self.findings)

    def to_dict(self) -> dict[str, object]:
        return {
            "root": str(self.root),
            "score": self.score,
            "rules_run": self.rules_run,
            "counts": self.counts,
            "findings": [item.to_dict() for item in self.findings],
        }
