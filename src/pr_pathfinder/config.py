"""Optional per-repository configuration (`pr-pathfinder.toml`)."""

from __future__ import annotations

import tomllib
from dataclasses import dataclass
from pathlib import Path

from pr_pathfinder.models import Severity
from pr_pathfinder.rules import builtin_rules

CONFIG_FILENAME = "pr-pathfinder.toml"


@dataclass(frozen=True, slots=True)
class Config:
    """Parsed repository configuration."""

    include: tuple[str, ...] | None = None
    ignore: tuple[str, ...] = ()
    severity_overrides: tuple[tuple[str, Severity], ...] = ()


def load_config(root: Path) -> Config:
    """Read the optional config file; a missing file means defaults.

    Raises ValueError with a human-readable message on invalid content.
    """

    candidate = root.expanduser().resolve() / CONFIG_FILENAME
    if not candidate.is_file():
        return Config()

    try:
        data = tomllib.loads(candidate.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError) as exc:
        raise ValueError(f"Invalid {CONFIG_FILENAME}: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError(f"Invalid {CONFIG_FILENAME}: expected a TOML document")

    allowed_keys = {"include", "ignore", "severity"}
    unknown_keys = sorted(set(data) - allowed_keys)
    if unknown_keys:
        raise ValueError(
            f"Invalid {CONFIG_FILENAME}: unknown settings: {', '.join(unknown_keys)}. "
            "Expected: include, ignore, severity."
        )

    raw_include = data.get("include")
    if raw_include is not None and (
        not isinstance(raw_include, list) or not all(isinstance(item, str) for item in raw_include)
    ):
        raise ValueError(f"Invalid {CONFIG_FILENAME}: 'include' must be a list of rule ids")

    raw_ignore = data.get("ignore", [])
    if not isinstance(raw_ignore, list) or not all(isinstance(item, str) for item in raw_ignore):
        raise ValueError(f"Invalid {CONFIG_FILENAME}: 'ignore' must be a list of rule ids")

    known_ids = {rule.rule_id for rule in builtin_rules()}
    unknown_include = (
        [] if raw_include is None else [item for item in raw_include if item not in known_ids]
    )
    if unknown_include:
        raise ValueError(
            f"Invalid {CONFIG_FILENAME}: unknown rule ids in 'include': "
            f"{', '.join(unknown_include)}. "
            "Run `pr-pathfinder rules` to list valid identifiers."
        )

    unknown = [item for item in raw_ignore if item not in known_ids]
    if unknown:
        raise ValueError(
            f"Invalid {CONFIG_FILENAME}: unknown rule ids: {', '.join(unknown)}. "
            "Run `pr-pathfinder rules` to list valid identifiers."
        )

    raw_severity = data.get("severity", {})
    if not isinstance(raw_severity, dict) or not all(
        isinstance(rule_id, str) and isinstance(level, str)
        for rule_id, level in raw_severity.items()
    ):
        raise ValueError(
            f"Invalid {CONFIG_FILENAME}: 'severity' must map rule ids to severity names"
        )

    unknown_severity_ids = sorted(set(raw_severity) - known_ids)
    if unknown_severity_ids:
        raise ValueError(
            f"Invalid {CONFIG_FILENAME}: unknown rule ids in 'severity': "
            f"{', '.join(unknown_severity_ids)}. "
            "Run `pr-pathfinder rules` to list valid identifiers."
        )

    severity_overrides: list[tuple[str, Severity]] = []
    for rule_id, level in sorted(raw_severity.items()):
        try:
            severity_overrides.append((rule_id, Severity.parse(level)))
        except ValueError as exc:
            choices = ", ".join(item.name.lower() for item in Severity)
            raise ValueError(
                f"Invalid {CONFIG_FILENAME}: severity for {rule_id!r} must be one of: {choices}"
            ) from exc

    return Config(
        include=None if raw_include is None else tuple(dict.fromkeys(raw_include)),
        ignore=tuple(dict.fromkeys(raw_ignore)),
        severity_overrides=tuple(severity_overrides),
    )
