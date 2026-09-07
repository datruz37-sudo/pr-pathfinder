import json
from pathlib import Path

from pr_pathfinder.reporters import render_sarif
from pr_pathfinder.scanner import scan_repository

FIXTURES = Path(__file__).parent / "fixtures"


def test_sarif_output_has_required_document_structure() -> None:
    payload = json.loads(render_sarif(scan_repository(FIXTURES / "minimal")))

    assert payload["$schema"] == "https://json.schemastore.org/sarif-2.1.0.json"
    assert payload["version"] == "2.1.0"
    run = payload["runs"][0]
    assert run["tool"]["driver"]["name"] == "pr-pathfinder"
    assert run["results"]
    assert all("ruleId" in result and "locations" in result for result in run["results"])


def test_sarif_output_represents_empty_scan() -> None:
    payload = json.loads(render_sarif(scan_repository(FIXTURES / "healthy")))

    run = payload["runs"][0]
    assert run["results"] == []
    assert run["tool"]["driver"]["rules"] == []
