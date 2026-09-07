"""Built-in rule registry."""

from __future__ import annotations

from pr_pathfinder.models import Rule
from pr_pathfinder.rules.agentready import RULES as AGENTREADY_RULES
from pr_pathfinder.rules.automation import RULES as AUTOMATION_RULES
from pr_pathfinder.rules.community import RULES as COMMUNITY_RULES
from pr_pathfinder.rules.ecosystem import RULES as ECOSYSTEM_RULES


def builtin_rules() -> tuple[Rule, ...]:
    """Return built-in rules in stable order."""

    rules = (*COMMUNITY_RULES, *AUTOMATION_RULES, *AGENTREADY_RULES, *ECOSYSTEM_RULES)
    identifiers = [rule.rule_id for rule in rules]
    if len(identifiers) != len(set(identifiers)):
        raise RuntimeError("Duplicate built-in rule identifier")
    return rules
