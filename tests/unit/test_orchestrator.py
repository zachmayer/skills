"""Tests for heartbeat orchestrator pure helpers."""

import importlib.util
from pathlib import Path
from unittest.mock import patch

SCRIPT = (
    Path(__file__).resolve().parents[2]
    / ".claude"
    / "skills"
    / "heartbeat"
    / "scripts"
    / "orchestrator.py"
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


def test_log_path():
    path = orchestrator.log_path("zachmayer/skills", 42)
    assert path == Path.home() / ".claude" / "heartbeat-skills-42.log"


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


def test_set_label_add_only():
    """set_label with only add should not include --remove-label."""
    with patch.object(orchestrator, "run") as mock_run:
        orchestrator.set_label("owner/repo", 42, "ai:coding")
        cmd = mock_run.call_args[0][0]
        assert "--add-label" in cmd
        assert "ai:coding" in cmd
        assert "--remove-label" not in cmd


def test_set_label_add_and_remove():
    """set_label with add and remove should include both flags."""
    with patch.object(orchestrator, "run") as mock_run:
        orchestrator.set_label("owner/repo", 42, "ai:coding", remove="ai:queued")
        cmd = mock_run.call_args[0][0]
        assert "--add-label" in cmd
        assert "--remove-label" in cmd


def test_set_label_remove_only():
    """set_label with only remove should not include --add-label."""
    with patch.object(orchestrator, "run") as mock_run:
        orchestrator.set_label("owner/repo", 42, remove="ai:coding,ai:queued")
        cmd = mock_run.call_args[0][0]
        assert "--remove-label" in cmd
        assert "--add-label" not in cmd


def test_set_label_noop():
    """set_label with neither add nor remove should not run anything."""
    with patch.object(orchestrator, "run") as mock_run:
        orchestrator.set_label("owner/repo", 42)
        mock_run.assert_not_called()


def test_set_label_uses_list_form():
    """set_label should pass a list to run(), not a string (no shell)."""
    with patch.object(orchestrator, "run") as mock_run:
        orchestrator.set_label("owner/repo", 42, "ai:coding")
        cmd = mock_run.call_args[0][0]
        assert isinstance(cmd, list)


def test_find_related_prs_merges_sources():
    """find_related_prs deduplicates PRs from search and branch queries."""
    pr_a = {"number": 100, "state": "CLOSED", "title": "A", "headRefName": "fix/a"}
    pr_b = {"number": 200, "state": "OPEN", "title": "B", "headRefName": "ai/issue-5"}
    pr_dup = {"number": 100, "state": "CLOSED", "title": "A", "headRefName": "fix/a"}

    with patch.object(orchestrator, "gh_json") as mock_gh:
        mock_gh.side_effect = [
            [pr_a, pr_b],  # by_search
            [pr_dup],  # by_branch
        ]
        all_prs, most_recent_open = orchestrator.find_related_prs("owner/repo", 5)

    assert len(all_prs) == 2
    assert most_recent_open == 200


def test_find_related_prs_empty():
    """find_related_prs returns empty results when no PRs found."""
    with patch.object(orchestrator, "gh_json") as mock_gh:
        mock_gh.side_effect = [None, None]
        all_prs, most_recent_open = orchestrator.find_related_prs("owner/repo", 999)

    assert all_prs == []
    assert most_recent_open is None


def test_find_related_prs_no_open():
    """find_related_prs returns None for most_recent_open when all PRs are closed."""
    pr = {"number": 100, "state": "CLOSED", "title": "A", "headRefName": "fix/a"}
    with patch.object(orchestrator, "gh_json") as mock_gh:
        mock_gh.side_effect = [[pr], []]
        all_prs, most_recent_open = orchestrator.find_related_prs("owner/repo", 5)

    assert len(all_prs) == 1
    assert most_recent_open is None


def test_build_context_queue():
    """build_context strips frontmatter and substitutes variables."""
    ctx = orchestrator.build_context(
        "queue",
        issue_number=42,
        repo="zachmayer/skills",
        issue_title="Test issue",
        issue_body="Do the thing",
        related_prs="None",
    )
    assert "Issue #42" in ctx
    assert "zachmayer/skills" in ctx
    assert "Test issue" in ctx
    assert "Do the thing" in ctx
    # Frontmatter should be stripped
    assert "---" not in ctx
    assert "maxTurns" not in ctx
    # Result file path should be substituted
    assert "queue-result-42.txt" in ctx


def test_build_context_coding():
    """build_context for coding agent includes all fields."""
    ctx = orchestrator.build_context(
        "coding",
        issue_number=99,
        repo="zachmayer/skills",
        issue_title="Test issue",
        issue_body="Body text",
        pr_number=100,
        branch="ai/issue-99",
        related_prs="#100, #200",
        feedback="Fix the bug",
        ci_status="All passing",
        branch_status="Up to date with main",
    )
    assert "Issue #99" in ctx
    assert "#100" in ctx
    assert "ai/issue-99" in ctx
    assert "#100, #200" in ctx
    assert "Fix the bug" in ctx
    assert "All passing" in ctx


def test_build_context_review():
    """build_context for review agent substitutes PR number."""
    ctx = orchestrator.build_context(
        "review",
        issue_number=42,
        repo="zachmayer/skills",
        issue_title="Test issue",
        issue_body="Body",
        pr_number=100,
    )
    assert "PR #100" in ctx
    assert "Issue #42" in ctx
    assert "--comment" in ctx  # review agent uses --comment, not --approve


def test_build_related_prs_context_empty():
    """build_related_prs_context returns 'None' for empty PRs."""
    result = orchestrator.build_related_prs_context([], None, "owner/repo")
    assert result == "None"


def test_build_related_prs_context_with_prs():
    """build_related_prs_context formats PR numbers and instructions."""
    prs = [
        {"number": 100, "state": "CLOSED", "title": "A", "headRefName": "fix/a"},
        {"number": 200, "state": "OPEN", "title": "B", "headRefName": "ai/issue-5"},
    ]
    result = orchestrator.build_related_prs_context(prs, 200, "owner/repo")
    assert "#100" in result
    assert "#200" in result
    assert "Most recent: #200" in result
    assert "Most recent open: #200" in result
    assert "gh pr view" in result


def test_has_diff_with_commits():
    """has_diff returns True when branch has commits beyond main."""
    with patch.object(orchestrator, "run") as mock_run:
        mock_run.return_value.stdout = "3\n"
        mock_run.return_value.returncode = 0
        result = orchestrator.has_diff("/some/path")
        cmd = mock_run.call_args[0][0]
        assert "rev-list" in cmd
        assert "origin/main..HEAD" in cmd
        assert result is True


def test_has_diff_no_commits():
    """has_diff returns False when branch has no commits beyond main."""
    with patch.object(orchestrator, "run") as mock_run:
        mock_run.return_value.stdout = "0\n"
        mock_run.return_value.returncode = 0
        result = orchestrator.has_diff("/some/path")
        assert result is False


def test_get_default_owner_from_codeowners(tmp_path, monkeypatch):
    """get_default_owner reads the * rule from CODEOWNERS."""
    codeowners_dir = tmp_path / ".github"
    codeowners_dir.mkdir()
    (codeowners_dir / "CODEOWNERS").write_text("# comment\n* @alice\n.github/ @bob\n")
    monkeypatch.setattr(orchestrator, "repo_dir", lambda repo: tmp_path)
    assert orchestrator.get_default_owner("org/repo") == "alice"


def test_get_default_owner_fallback():
    """get_default_owner falls back to repo owner when no CODEOWNERS."""
    assert orchestrator.get_default_owner("zachmayer/skills") == "zachmayer"
    assert orchestrator.get_default_owner("org/my-repo") == "org"


# --- resolve_working_branch ---


def test_resolve_working_branch_with_open_pr():
    """resolve_working_branch returns the open PR's branch when one exists."""
    all_prs = [
        {"number": 10, "state": "CLOSED", "headRefName": "old-branch"},
        {"number": 20, "state": "OPEN", "headRefName": "feature-branch"},
    ]
    assert orchestrator.resolve_working_branch(all_prs, 20, "ai/issue-5") == "feature-branch"


def test_resolve_working_branch_no_open_pr():
    """resolve_working_branch returns canonical when no open PR."""
    all_prs = [{"number": 10, "state": "CLOSED", "headRefName": "old-branch"}]
    assert orchestrator.resolve_working_branch(all_prs, None, "ai/issue-5") == "ai/issue-5"


def test_resolve_working_branch_empty():
    """resolve_working_branch returns canonical when no PRs at all."""
    assert orchestrator.resolve_working_branch([], None, "ai/issue-5") == "ai/issue-5"


# --- ensure_pr (simplified) ---


def test_ensure_pr_signature():
    """ensure_pr takes 3 args (no all_prs/most_recent_open)."""
    import inspect

    sig = inspect.signature(orchestrator.ensure_pr)
    params = list(sig.parameters.keys())
    assert params == ["repo", "issue", "canonical_branch"]


# --- process_queue ---

FAKE_ISSUE = {"number": 42, "title": "Test issue", "body": "Do the thing"}


def test_process_queue_actionable(tmp_path, monkeypatch):
    """process_queue moves to ai:coding when agent writes 'actionable'."""
    monkeypatch.setattr(orchestrator, "SCRATCH_DIR", tmp_path)
    monkeypatch.setattr(orchestrator, "find_related_prs", lambda *a: ([], None))
    monkeypatch.setattr(orchestrator, "build_related_prs_context", lambda *a: "None")

    def fake_invoke(agent, workdir, ctx, num, repo, *, budget=8):
        (tmp_path / f"queue-result-{num}.txt").write_text("actionable\n")
        return 0

    monkeypatch.setattr(orchestrator, "invoke_agent", fake_invoke)

    labels_set = []
    monkeypatch.setattr(
        orchestrator,
        "set_label",
        lambda repo, num, add=None, remove=None: labels_set.append((add, remove)),
    )

    process_queue = orchestrator.process_queue
    process_queue("owner/repo", tmp_path, FAKE_ISSUE)

    assert labels_set == [("ai:coding", "ai:queued")]


def test_process_queue_blocked(tmp_path, monkeypatch):
    """process_queue removes labels when agent writes 'blocked'."""
    monkeypatch.setattr(orchestrator, "SCRATCH_DIR", tmp_path)
    monkeypatch.setattr(orchestrator, "find_related_prs", lambda *a: ([], None))
    monkeypatch.setattr(orchestrator, "build_related_prs_context", lambda *a: "None")

    def fake_invoke(agent, workdir, ctx, num, repo, *, budget=8):
        (tmp_path / f"queue-result-{num}.txt").write_text("blocked\n")
        return 0

    monkeypatch.setattr(orchestrator, "invoke_agent", fake_invoke)

    labels_removed = []
    monkeypatch.setattr(
        orchestrator,
        "set_label",
        lambda repo, num, add=None, remove=None: labels_removed.append((add, remove)),
    )

    orchestrator.process_queue("owner/repo", tmp_path, FAKE_ISSUE)

    # remove_ai_labels calls set_label with remove only
    assert labels_removed == [(None, "ai:coding,ai:queued,ai:review")]


def test_process_queue_crash(tmp_path, monkeypatch):
    """process_queue removes labels and posts comment on agent crash."""
    monkeypatch.setattr(orchestrator, "SCRATCH_DIR", tmp_path)
    monkeypatch.setattr(orchestrator, "find_related_prs", lambda *a: ([], None))
    monkeypatch.setattr(orchestrator, "build_related_prs_context", lambda *a: "None")
    monkeypatch.setattr(orchestrator, "invoke_agent", lambda *a, **kw: 1)

    labels_removed = []
    monkeypatch.setattr(
        orchestrator,
        "set_label",
        lambda repo, num, add=None, remove=None: labels_removed.append((add, remove)),
    )
    comments = []
    monkeypatch.setattr(orchestrator, "gh_comment", lambda repo, num, body: comments.append(body))

    orchestrator.process_queue("owner/repo", tmp_path, FAKE_ISSUE)

    assert labels_removed == [(None, "ai:coding,ai:queued,ai:review")]
    assert len(comments) == 1
    assert "crashed" in comments[0]


def test_process_queue_no_result_file(tmp_path, monkeypatch):
    """process_queue defaults to 'actionable' when no result file written."""
    monkeypatch.setattr(orchestrator, "SCRATCH_DIR", tmp_path)
    monkeypatch.setattr(orchestrator, "find_related_prs", lambda *a: ([], None))
    monkeypatch.setattr(orchestrator, "build_related_prs_context", lambda *a: "None")
    monkeypatch.setattr(orchestrator, "invoke_agent", lambda *a, **kw: 0)

    labels_set = []
    monkeypatch.setattr(
        orchestrator,
        "set_label",
        lambda repo, num, add=None, remove=None: labels_set.append((add, remove)),
    )

    orchestrator.process_queue("owner/repo", tmp_path, FAKE_ISSUE)

    # Default is actionable — move to coding
    assert labels_set == [("ai:coding", "ai:queued")]
