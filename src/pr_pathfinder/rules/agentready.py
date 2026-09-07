"""Rules for readers that meet a repository through an automated assistant.

Every rule in this module is evaluated from a single checkout: no network
calls, no subprocesses, no model inference, and no execution of code found in
the inspected repository. A rule only reports something it can point at, so a
finding can always be traced back to a file.
"""

from __future__ import annotations

import re

from pr_pathfinder.models import Finding, Rule, RuleContext, Severity
from pr_pathfinder.rules.base import RequiredFileRule

# Directories that never represent project content worth reading as text.
_SKIP_DIRS = frozenset(
    {
        ".git",
        ".hg",
        ".svn",
        ".tox",
        ".venv",
        "venv",
        "__pycache__",
        "node_modules",
        "site-packages",
        "dist",
        "build",
        "target",
        ".mypy_cache",
        ".pytest_cache",
        ".ruff_cache",
        ".aider",
        ".aider.chat.history.md",
        ".aider.input.history",
        ".continue",
        ".cursorignore",
        ".windsurf",
    }
)

# Files an automated reader would ingest as text when trying to understand a
# project. Binaries are excluded on purpose: a large image is not a context
# problem in the same way a large source file is.
_TEXT_SUFFIXES = frozenset(
    {
        ".c",
        ".cfg",
        ".cpp",
        ".css",
        ".go",
        ".h",
        ".html",
        ".ini",
        ".java",
        ".js",
        ".json",
        ".jsx",
        ".kt",
        ".md",
        ".py",
        ".rb",
        ".rs",
        ".rst",
        ".sql",
        ".toml",
        ".ts",
        ".tsx",
        ".txt",
        ".xml",
        ".yaml",
        ".yml",
    }
)

# Roughly 50k tokens of text, a size that forces an assistant to guess instead
# of read. The threshold is a constant so behaviour is identical everywhere.
_LARGE_FILE_BYTES = 200_000

_REPORTED_LARGE_FILES = 3


class ContextBudgetRule:
    """Flag text files too large for an assistant to read in one pass."""

    rule_id = "agentready/context-budget"
    summary = "No single text file is too large to be read at once"

    def check(self, context: RuleContext) -> list[Finding]:
        oversized: list[tuple[str, int]] = []
        for path in sorted(context.root.rglob("*")):
            if not path.is_file():
                continue
            if any(part in _SKIP_DIRS for part in path.relative_to(context.root).parts):
                continue
            if path.suffix.lower() not in _TEXT_SUFFIXES:
                continue
            size = path.stat().st_size
            if size > _LARGE_FILE_BYTES:
                oversized.append((str(path.relative_to(context.root)), size))

        oversized.sort(key=lambda item: item[1], reverse=True)
        findings = []
        for relative_path, size in oversized[:_REPORTED_LARGE_FILES]:
            findings.append(
                Finding(
                    rule_id=self.rule_id,
                    severity=Severity.WARNING,
                    title="File is too large to be read in one pass",
                    detail=(
                        f"{relative_path} is {size:,} bytes (roughly {size // 4:,} tokens). "
                        "A reader has to guess what is inside instead of reading it."
                    ),
                    recommendation=(
                        "Split the file, move reference material into a separate document, or "
                        "point to the sections that matter from a shorter index file."
                    ),
                    path=relative_path,
                )
            )
        return findings


class DocumentedMakeTargetsRule:
    """Flag documentation that tells the reader to run make without a Makefile."""

    rule_id = "agentready/documented-make-targets"
    summary = "Documented make targets are backed by a Makefile"

    _target = re.compile(r"\bmake\s+([A-Za-z0-9_][A-Za-z0-9_.-]*)")
    _fenced = re.compile(r"```.*?```", re.DOTALL)
    _inline = re.compile(r"`[^`\n]+`")
    _docs = ("README.md", "CONTRIBUTING.md", ".github/CONTRIBUTING.md")

    @classmethod
    def _commands(cls, content: str) -> str:
        """Return only the text a reader is told to type.

        Prose is excluded on purpose: a sentence such as "helping make open
        source easier" is not a build target, and flagging it would make the
        rule unusable.
        """

        fenced = cls._fenced.findall(content)
        inline = cls._inline.findall(cls._fenced.sub("", content))
        return "\n".join([*fenced, *inline])

    def check(self, context: RuleContext) -> list[Finding]:
        for document in self._docs:
            path, content = context.read_first(document)
            if path is None:
                continue
            targets = sorted(set(self._target.findall(self._commands(content))))
            if not targets:
                continue
            if context.exists_any("Makefile", "makefile", "GNUmakefile"):
                return []
            return [
                Finding(
                    rule_id=self.rule_id,
                    severity=Severity.WARNING,
                    title="Documented make targets have no Makefile",
                    detail=(
                        f"{path} tells the reader to run: {', '.join(targets)}. "
                        "No Makefile is present to define them."
                    ),
                    recommendation=(
                        "Add the Makefile, or replace the instructions with the commands a "
                        "contributor can actually run."
                    ),
                    path=path,
                )
            ]
        return []


RULES: tuple[Rule, ...] = (
    RequiredFileRule(
        rule_id="agentready/instructions",
        summary="Repository carries instructions for automated readers",
        paths=("AGENTS.md", "CLAUDE.md", ".github/AGENTS.md", ".github/CLAUDE.md"),
        title="No instructions for automated readers",
        detail=(
            "An assistant entering this repository has no statement of the build, test, and "
            "style conventions to follow, so it has to infer them from every file."
        ),
        recommendation=(
            "Add AGENTS.md or CLAUDE.md with the commands to set up, test, and lint the project."
        ),
        severity=Severity.WARNING,
    ),
    ContextBudgetRule(),
    DocumentedMakeTargetsRule(),
)
