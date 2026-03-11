"""Integration tests for heartbeat orchestrator — hits real GitHub APIs.

These tests FAIL (not skip) when `gh auth status` fails, because they
validate real GitHub behavior that unit mocks can't catch.
"""

import importlib.util
import subprocess
from pathlib import Path

import pytest

SCRIPT = (
    Path(__file__).resolve().parents[2] / "skills" / "heartbeat" / "scripts" / "orchestrator.py"
)
spec = importlib.util.spec_from_file_location("orchestrator", SCRIPT)
orchestrator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(orchestrator)

REPO = "zachmayer/skills"


@pytest.fixture(autouse=True, scope="module")
def require_gh_auth():
    """Fail the entire module if gh auth is not available."""
    result = subprocess.run(["gh", "auth", "status"], capture_output=True, text=True)
    if result.returncode != 0:
        pytest.fail("gh auth status failed — GitHub CLI not authenticated")


@pytest.mark.integration
def test_find_related_prs_issue_65():
    """Issue #65 should have >=3 related PRs (#121, #206, #258)."""
    all_prs, _most_recent_open = orchestrator.find_related_prs(REPO, 65)
    pr_numbers = {p["number"] for p in all_prs}
    assert len(all_prs) >= 3, f"Expected >=3 PRs, got {len(all_prs)}: {pr_numbers}"
    assert 121 in pr_numbers
    assert 206 in pr_numbers
    assert 258 in pr_numbers


@pytest.mark.integration
def test_find_related_prs_issue_194():
    """Issue #194 should have >=5 related PRs (validates #{N} search pattern)."""
    all_prs, _most_recent_open = orchestrator.find_related_prs(REPO, 194)
    pr_numbers = {p["number"] for p in all_prs}
    assert len(all_prs) >= 5, f"Expected >=5 PRs, got {len(all_prs)}: {pr_numbers}"


@pytest.mark.integration
def test_find_related_prs_nonexistent():
    """An issue with no PRs should return empty results."""
    all_prs, most_recent_open = orchestrator.find_related_prs(REPO, 999999)
    assert all_prs == []
    assert most_recent_open is None


@pytest.mark.integration
def test_get_feedback():
    """Issue #188 should have non-trivial feedback."""
    feedback = orchestrator.get_feedback(REPO, 188, None)
    assert feedback != "None", "Expected comments on issue #188"


@pytest.mark.integration
def test_get_ci_status():
    """A merged PR should have CI status."""
    status = orchestrator.get_ci_status(REPO, 258)
    assert isinstance(status, str)
    assert status != "No PR yet"
