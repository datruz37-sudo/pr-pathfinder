"""Rules for the human side of a contributor's first patch."""

from __future__ import annotations

import re

from pr_pathfinder.models import Finding, Rule, RuleContext, Severity
from pr_pathfinder.rules.base import RequiredFileRule


class ContributingContentRule:
    rule_id = "community/contributing-content"
    summary = "CONTRIBUTING explains setup, tests, and pull requests"

    _sections = {
        "setup": re.compile(r"\b(setup|install|development environment|getting started)\b", re.I),
        "tests": re.compile(r"\b(test|check|verify)\b", re.I),
        "pull requests": re.compile(r"\b(pull request|\bpr\b|submit)\b", re.I),
    }

    def check(self, context: RuleContext) -> list[Finding]:
        path, content = context.read_first("CONTRIBUTING.md", ".github/CONTRIBUTING.md")
        if path is None:
            return []
        missing = [name for name, pattern in self._sections.items() if not pattern.search(content)]
        if not missing:
            return []
        return [
            Finding(
                rule_id=self.rule_id,
                severity=Severity.WARNING,
                title="Contributor guide leaves steps implicit",
                detail=f"Missing guidance about: {', '.join(missing)}.",
                recommendation="Add short, copy-pasteable steps for every missing topic.",
                path=path,
            )
        ]


class CodeOfConductContactRule:
    rule_id = "community/code-of-conduct-contact"
    summary = "Code of conduct has a private reporting contact"

    _contact = re.compile(r"(?:mailto:|[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}|report.*privat)", re.I)

    def check(self, context: RuleContext) -> list[Finding]:
        path, content = context.read_first("CODE_OF_CONDUCT.md", ".github/CODE_OF_CONDUCT.md")
        if path is None or self._contact.search(content):
            return []
        return [
            Finding(
                rule_id=self.rule_id,
                severity=Severity.WARNING,
                title="Code of conduct lacks a private contact",
                detail="Contributors are told what behavior is expected but not where to report abuse.",
                recommendation="Add a monitored email address or private reporting form.",
                path=path,
            )
        ]


RULES: tuple[Rule, ...] = (
    RequiredFileRule(
        rule_id="community/readme",
        summary="Repository includes a README",
        paths=("README.md", "README.rst", "README.txt"),
        title="README is missing",
        detail="A newcomer cannot quickly understand the project's purpose.",
        recommendation="Add a README with purpose, status, installation, and a minimal example.",
    ),
    RequiredFileRule(
        rule_id="community/license",
        summary="Repository declares an open-source license",
        paths=("LICENSE", "LICENSE.md", "COPYING"),
        title="License is missing",
        detail="Potential contributors cannot determine how the project may be reused.",
        recommendation="Choose an OSI-approved license and add its full text.",
    ),
    RequiredFileRule(
        rule_id="community/contributing",
        summary="Repository includes a contributor guide",
        paths=("CONTRIBUTING.md", ".github/CONTRIBUTING.md"),
        title="Contributor guide is missing",
        detail="The path from clone to pull request is undocumented.",
        recommendation="Add CONTRIBUTING.md with setup, test, style, and review steps.",
    ),
    RequiredFileRule(
        rule_id="community/code-of-conduct",
        summary="Repository includes a code of conduct",
        paths=("CODE_OF_CONDUCT.md", ".github/CODE_OF_CONDUCT.md"),
        title="Code of conduct is missing",
        detail="Community behavior and enforcement expectations are unclear.",
        recommendation="Adopt a recognized code of conduct and provide a private contact.",
        severity=Severity.WARNING,
    ),
    RequiredFileRule(
        rule_id="community/security",
        summary="Repository explains private vulnerability reporting",
        paths=("SECURITY.md", ".github/SECURITY.md"),
        title="Security policy is missing",
        detail="Researchers do not have a safe path for reporting vulnerabilities.",
        recommendation="Add SECURITY.md with supported versions and a private reporting route.",
        severity=Severity.WARNING,
    ),
    ContributingContentRule(),
    CodeOfConductContactRule(),
)
