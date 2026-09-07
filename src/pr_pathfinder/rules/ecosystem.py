"""Rules that check documented commands against the project files behind them.

A contributor guide that tells a newcomer to run a command which cannot work is
worse than no guide: it turns the first contribution into an error message.
These rules stay conservative — they only judge a repository when the files
that would back the command (a Python packaging manifest or a `package.json`)
actually exist, and every check is a local read of the checkout.
"""

from __future__ import annotations

import json
import re

from pr_pathfinder.models import Finding, Rule, RuleContext, Severity

_DOCS = ("README.md", "CONTRIBUTING.md", ".github/CONTRIBUTING.md")

_fenced = re.compile(r"```.*?```", re.DOTALL)
_inline = re.compile(r"`[^`\n]+`")


def _command_text(content: str) -> str:
    """Return only the text a reader is told to type, fenced blocks first."""

    fenced = _fenced.findall(content)
    inline = _inline.findall(_fenced.sub("", content))
    return "\n".join([*fenced, *inline])


class NodeScriptsRule:
    """Report npm scripts a document tells the reader to run but that do not exist."""

    rule_id = "ecosystem/node-scripts"
    summary = "Documented npm scripts exist in package.json"

    _run = re.compile(r"\bnpm\s+run\s+([A-Za-z0-9:_-]+)")
    _test = re.compile(r"\bnpm\s+test\b")

    def check(self, context: RuleContext) -> list[Finding]:
        manifest = context.root / "package.json"
        if not manifest.is_file():
            return []
        try:
            data = json.loads(manifest.read_text(encoding="utf-8", errors="replace"))
        except (json.JSONDecodeError, OSError):
            return []
        scripts = data.get("scripts") if isinstance(data, dict) else None
        if not isinstance(scripts, dict):
            scripts = {}

        findings: list[Finding] = []
        for document in _DOCS:
            path, content = context.read_first(document)
            if path is None:
                continue
            commands = _command_text(content)
            documented = sorted(
                set(self._run.findall(commands))
                | ({"test"} if self._test.search(commands) else set())
            )
            missing = [name for name in documented if name not in scripts]
            if not missing:
                continue
            findings.append(
                Finding(
                    rule_id=self.rule_id,
                    severity=Severity.WARNING,
                    title="Documented npm scripts are missing",
                    detail=(
                        f"{path} tells the reader to run: {', '.join(missing)}. "
                        f"package.json defines no such script, so the command fails."
                    ),
                    recommendation=(
                        "Add the script to package.json, or replace the instruction with the "
                        "command a contributor can actually run."
                    ),
                    path=path,
                )
            )
        return findings


class PythonDevToolsRule:
    """Report documented dev tools that no project file declares."""

    rule_id = "ecosystem/python-dev-tools"
    summary = "Documented Python dev tools are declared by the project"

    _tools = ("pytest", "ruff", "mypy", "black", "flake8", "isort", "tox", "nox", "coverage")
    _manifests = (
        "pyproject.toml",
        "setup.py",
        "setup.cfg",
        "tox.ini",
        "Makefile",
        "Pipfile",
        "noxfile.py",
    )

    def check(self, context: RuleContext) -> list[Finding]:
        if not context.exists_any(*self._manifests):
            return []
        declared_names: set[str] = set()
        for manifest in self._manifests:
            for candidate in context.root.glob(manifest):
                text = candidate.read_text(encoding="utf-8", errors="replace").lower()
                declared_names |= {name for name in self._tools if name in text}
        for candidate in sorted(context.root.glob("requirements*.txt")):
            text = candidate.read_text(encoding="utf-8", errors="replace").lower()
            declared_names |= {name for name in self._tools if name in text}

        findings: list[Finding] = []
        for document in _DOCS:
            path, content = context.read_first(document)
            if path is None:
                continue
            commands = _command_text(content)
            missing = []
            for tool in self._tools:
                pattern = re.compile(rf"(?<![\w-])(?:python\s+-m\s+)?{tool}(?![\w-])")
                if not pattern.search(commands):
                    continue
                if tool in declared_names:
                    continue
                if self._installed_inline(commands, tool):
                    continue
                missing.append(tool)
            if not missing:
                continue
            findings.append(
                Finding(
                    rule_id=self.rule_id,
                    severity=Severity.WARNING,
                    title="Documented dev tools are not declared",
                    detail=(
                        f"{path} tells the reader to run: {', '.join(missing)}. No packaging "
                        "file in the repository declares them, so a clean environment fails "
                        "with command not found."
                    ),
                    recommendation=(
                        "Add the tools to a dev extra in pyproject.toml (or a requirements "
                        "file), or document the exact install command next to their use."
                    ),
                    path=path,
                )
            )
        return findings

    @staticmethod
    def _installed_inline(commands: str, tool: str) -> bool:
        """Treat a documented `pip install ... <tool>` as covered."""

        for line in commands.splitlines():
            if "pip install" in line and re.search(rf"(?<![\w-]){tool}(?![\w-])", line):
                return True
        return False


RULES: tuple[Rule, ...] = (
    NodeScriptsRule(),
    PythonDevToolsRule(),
)
