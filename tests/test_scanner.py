from pathlib import Path

from pr_pathfinder.models import Severity
from pr_pathfinder.scanner import scan_repository


FIXTURES = Path(__file__).parent / "fixtures"


def test_minimal_repository_reports_core_blockers() -> None:
    result = scan_repository(FIXTURES / "minimal")

    rule_ids = {finding.rule_id for finding in result.findings}
    assert "community/license" in rule_ids
    assert "community/contributing" in rule_ids
    assert "automation/continuous-integration" in rule_ids
    assert result.score < 100
    assert result.should_fail(Severity.ERROR)


def test_healthy_repository_has_no_findings() -> None:
    result = scan_repository(FIXTURES / "healthy")

    assert result.findings == ()
    assert result.score == 100
    assert not result.should_fail(Severity.INFO)


def test_counts_include_every_severity() -> None:
    result = scan_repository(FIXTURES / "minimal")

    assert set(result.counts) == {"info", "warning", "error"}
    assert sum(result.counts.values()) == len(result.findings)
