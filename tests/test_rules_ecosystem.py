from pathlib import Path

from pr_pathfinder.models import RuleContext
from pr_pathfinder.rules.ecosystem import NodeScriptsRule, PythonDevToolsRule

FIXTURES = Path(__file__).parent / "fixtures"


def test_node_scripts_missing_script_fires(tmp_path: Path) -> None:
    (tmp_path / "package.json").write_text(
        '{"name": "demo", "scripts": {"build": "echo build"}}', encoding="utf-8"
    )
    (tmp_path / "CONTRIBUTING.md").write_text(
        "# Contributing\n\n```sh\nnpm run build\nnpm run test\n```\n", encoding="utf-8"
    )

    findings = NodeScriptsRule().check(RuleContext(root=tmp_path))

    assert [finding.rule_id for finding in findings] == ["ecosystem/node-scripts"]
    assert "test" in findings[0].detail


def test_node_scripts_all_present_passes(tmp_path: Path) -> None:
    (tmp_path / "package.json").write_text(
        '{"scripts": {"build": "echo build", "test": "node --test"}}', encoding="utf-8"
    )
    (tmp_path / "CONTRIBUTING.md").write_text(
        "# Contributing\n\n```sh\nnpm run build\nnpm test\n```\n", encoding="utf-8"
    )

    assert NodeScriptsRule().check(RuleContext(root=tmp_path)) == []


def test_node_scripts_no_manifest_is_silent(tmp_path: Path) -> None:
    (tmp_path / "CONTRIBUTING.md").write_text(
        "Run `npm run test` before submitting.\n", encoding="utf-8"
    )

    assert NodeScriptsRule().check(RuleContext(root=tmp_path)) == []


def test_node_scripts_inline_commands_are_checked(tmp_path: Path) -> None:
    (tmp_path / "package.json").write_text('{"scripts": {}}', encoding="utf-8")
    (tmp_path / "README.md").write_text("Install, then run `npm run lint`.\n", encoding="utf-8")

    findings = NodeScriptsRule().check(RuleContext(root=tmp_path))

    assert [finding.rule_id for finding in findings] == ["ecosystem/node-scripts"]
    assert "lint" in findings[0].detail


def test_python_dev_tools_undeclared_fires(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text(
        '[project]\nname = "demo"\ndependencies = []\n', encoding="utf-8"
    )
    (tmp_path / "CONTRIBUTING.md").write_text(
        "# Contributing\n\n```sh\npytest\nruff check .\n```\n", encoding="utf-8"
    )

    findings = PythonDevToolsRule().check(RuleContext(root=tmp_path))

    assert [finding.rule_id for finding in findings] == ["ecosystem/python-dev-tools"]
    assert "pytest" in findings[0].detail
    assert "ruff" in findings[0].detail


def test_python_dev_tools_declared_passes(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text(
        '[project]\nname = "demo"\n[project.optional-dependencies]\ndev = ["pytest"]\n',
        encoding="utf-8",
    )
    (tmp_path / "CONTRIBUTING.md").write_text(
        "# Contributing\n\n```sh\npytest\n```\n", encoding="utf-8"
    )

    assert PythonDevToolsRule().check(RuleContext(root=tmp_path)) == []


def test_python_dev_tools_pip_install_documented_passes(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text('[project]\nname = "demo"\n', encoding="utf-8")
    (tmp_path / "CONTRIBUTING.md").write_text(
        "# Contributing\n\n```sh\npip install ruff\nruff check .\n```\n", encoding="utf-8"
    )

    assert PythonDevToolsRule().check(RuleContext(root=tmp_path)) == []


def test_python_dev_tools_no_manifest_is_silent(tmp_path: Path) -> None:
    (tmp_path / "CONTRIBUTING.md").write_text(
        "Run `pytest` and `ruff check .`.\n", encoding="utf-8"
    )

    assert PythonDevToolsRule().check(RuleContext(root=tmp_path)) == []
