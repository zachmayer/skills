"""Tests for heartbeat orchestrator pure helpers."""

import importlib.util
from pathlib import Path

SCRIPT = (
    Path(__file__).resolve().parents[2] / "skills" / "heartbeat" / "scripts" / "orchestrator.py"
)
spec = importlib.util.spec_from_file_location("orchestrator", SCRIPT)
orchestrator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(orchestrator)


def test_branch_name():
    assert orchestrator.branch_name(42) == "ai/issue-42"
    assert orchestrator.branch_name(1) == "ai/issue-1"


def test_worktree_path():
    path = orchestrator.worktree_path("zachmayer/skills", 42)
    assert path == Path.home() / "claude" / "worktrees" / "skills" / "ai-issue-42"


def test_worktree_path_nested_repo():
    path = orchestrator.worktree_path("org/sub-repo", 7)
    assert path == Path.home() / "claude" / "worktrees" / "sub-repo" / "ai-issue-7"


def test_build_prompt_substitution():
    prompt = orchestrator.build_prompt(
        issue_number=99,
        repo="zachmayer/skills",
        issue_title="Test issue",
        issue_body="Do the thing",
        pr_number=100,
        branch="ai/issue-99",
        prior_prs="None",
        human_feedback="None",
        ci_status="All passing",
        branch_status="Up to date with main",
    )
    assert "Issue #99" in prompt
    assert "zachmayer/skills" in prompt
    assert "Test issue" in prompt
    assert "Do the thing" in prompt
    assert "#100" in prompt
    assert "ai/issue-99" in prompt
    assert "All passing" in prompt
    assert "Up to date with main" in prompt


def test_load_repos_default(tmp_path, monkeypatch):
    monkeypatch.setattr(orchestrator, "REPOS_FILE", tmp_path / "nonexistent.conf")
    assert orchestrator.load_repos() == ["zachmayer/skills"]


def test_load_repos_from_file(tmp_path, monkeypatch):
    conf = tmp_path / "repos.conf"
    conf.write_text("# Comment\norg/repo1\norg/repo2\n\n")
    monkeypatch.setattr(orchestrator, "REPOS_FILE", conf)
    assert orchestrator.load_repos() == ["org/repo1", "org/repo2"]


def test_repo_dir():
    assert orchestrator.repo_dir("zachmayer/skills") == Path.home() / "source" / "skills"
    assert orchestrator.repo_dir("org/my-repo") == Path.home() / "source" / "my-repo"


def test_log_path_includes_repo():
    """Log files are namespaced by repo to avoid cross-repo collisions."""
    p1 = orchestrator.log_path("org/repo-a", 42)
    p2 = orchestrator.log_path("org/repo-b", 42)
    assert p1 != p2
    assert "repo-a" in str(p1)
    assert "repo-b" in str(p2)


def test_log_path_format():
    p = orchestrator.log_path("zachmayer/skills", 99)
    assert p.name == "heartbeat-skills-99.log"


def test_issue_author_default(monkeypatch):
    """ISSUE_AUTHOR defaults to zachmayer, configurable via env."""
    monkeypatch.delenv("HEARTBEAT_ISSUE_AUTHOR", raising=False)
    # Re-import to pick up env change
    spec2 = importlib.util.spec_from_file_location("orch2", SCRIPT)
    mod = importlib.util.module_from_spec(spec2)
    spec2.loader.exec_module(mod)
    assert mod.ISSUE_AUTHOR == "zachmayer"


def test_build_prompt_has_scoping_plan():
    """Worker prompt requires an execution plan before coding."""
    prompt = orchestrator.build_prompt(
        issue_number=1,
        repo="x/y",
        issue_title="t",
        issue_body="b",
        pr_number=2,
        branch="ai/issue-1",
        prior_prs="None",
        human_feedback="None",
        ci_status="All passing",
        branch_status="Up to date with main",
    )
    assert "execution plan" in prompt.lower()
    assert "acceptance criteria" in prompt.lower()


def test_build_prompt_no_makefile_in_constraints():
    """Makefile should NOT be in the constraints (contradiction fix)."""
    prompt = orchestrator.build_prompt(
        issue_number=1,
        repo="x/y",
        issue_title="t",
        issue_body="b",
        pr_number=2,
        branch="ai/issue-1",
        prior_prs="None",
        human_feedback="None",
        ci_status="All passing",
        branch_status="Up to date with main",
    )
    # Constraints section should not block Makefile edits
    constraints_start = prompt.find("## Constraints")
    constraints_section = prompt[constraints_start:] if constraints_start >= 0 else ""
    assert "Makefile" not in constraints_section


def test_build_prompt_lint_retry_cap():
    """Worker prompt includes max retry cap for lint/test to prevent infinite loops."""
    prompt = orchestrator.build_prompt(
        issue_number=1,
        repo="x/y",
        issue_title="t",
        issue_body="b",
        pr_number=2,
        branch="ai/issue-1",
        prior_prs="None",
        human_feedback="None",
        ci_status="All passing",
        branch_status="Up to date with main",
    )
    assert "max 3 attempts" in prompt.lower() or "3 attempts" in prompt.lower()
