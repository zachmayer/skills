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
