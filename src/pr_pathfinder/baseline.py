"""Baseline support: adopt gradually by suppressing already-known findings."""

from __future__ import annotations

import json
from collections.abc import Iterable
from pathlib import Path

from pr_pathfinder.models import Finding

BASELINE_VERSION = 1


def write_baseline(path: Path, findings: Iterable[Finding]) -> None:
    """Record finding fingerprints so a later scan reports only new ones."""

    fingerprints = sorted({finding.fingerprint() for finding in findings})
    document = {"version": BASELINE_VERSION, "findings": fingerprints}
    path.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")


def load_baseline(path: Path) -> frozenset[str]:
    """Load known fingerprints; raise ValueError with guidance on any problem."""

    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(
            f"Baseline file not found: {path}. "
            "Generate it with `pr-pathfinder check . --write-baseline <file>`."
        ) from exc
    except (OSError, ValueError) as exc:
        raise ValueError(f"Invalid baseline file {path}: {exc}") from exc

    if not isinstance(document, dict):
        raise ValueError(f"Invalid baseline file {path}: expected a JSON object")
    if document.get("version") != BASELINE_VERSION:
        raise ValueError(f"Invalid baseline file {path}: expected version {BASELINE_VERSION}")
    findings = document.get("findings", [])
    if not isinstance(findings, list) or not all(isinstance(item, str) for item in findings):
        raise ValueError(f"Invalid baseline file {path}: 'findings' must be a list of strings")
    return frozenset(findings)
