"""Optional per-repository configuration (`pr-pathfinder.toml`)."""

from __future__ import annotations

import tomllib
from dataclasses import dataclass
from pathlib import Path

from pr_pathfinder.rules import builtin_rules

CONFIG_FILENAME = "pr-pathfinder.toml"


@dataclass(frozen=True, slots=True)
class Config:
    """Parsed repository configuration."""

    ignore: tuple[str, ...] = ()


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

    raw_ignore = data.get("ignore", [])
    if not isinstance(raw_ignore, list) or not all(
        isinstance(item, str) for item in raw_ignore
    ):
        raise ValueError(f"Invalid {CONFIG_FILENAME}: 'ignore' must be a list of rule ids")

    known_ids = {rule.rule_id for rule in builtin_rules()}
    unknown = [item for item in raw_ignore if item not in known_ids]
    if unknown:
        raise ValueError(
            f"Invalid {CONFIG_FILENAME}: unknown rule ids: {', '.join(unknown)}. "
            "Run `pr-pathfinder rules` to list valid identifiers."
        )

    return Config(ignore=tuple(dict.fromkeys(raw_ignore)))
