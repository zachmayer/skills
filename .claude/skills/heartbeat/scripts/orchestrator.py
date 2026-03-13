#!/usr/bin/env python3
"""Heartbeat orchestrator: three-phase pipeline (queue → coding → review)."""

import fcntl
import json
import logging
import os
import string
import subprocess
from pathlib import Path

import click

MAX_ISSUES = 10
LOCK_FILE = Path.home() / ".claude" / "heartbeat.lock"
REPOS_FILE = Path.home() / ".claude" / "heartbeat-repos.conf"
OBSIDIAN_DIR = Path(os.environ.get("CLAUDE_OBSIDIAN_DIR", "~/claude/obsidian")).expanduser()
WORKTREE_BASE = Path.home() / "claude" / "worktrees"
SCRATCH_DIR = Path.home() / "claude" / "scratch"
LOG_DIR = Path.home() / ".claude"
SCRIPT_DIR = Path(__file__).parent
AGENT_DIR = SCRIPT_DIR.parent.parent.parent / "agents"

log = logging.getLogger("heartbeat")


# --- Helpers ---


def run(cmd, *, cwd=None, capture=False, check=True):
    """Run a command (list form, no shell)."""
    result = subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=capture,
        text=True,
    )
    if check and result.returncode != 0:
        raise subprocess.CalledProcessError(result.returncode, cmd, result.stdout, result.stderr)
    return result


def gh_json(cmd):
    """Run a gh command (list form) and parse JSON output. Returns parsed JSON or None."""
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0 or not result.stdout.strip():
        return None
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return None


def set_label(repo, issue_number, add=None, *, remove=None):
    """Set labels on an issue. Both add and remove are optional."""
    if not add and not remove:
        return
    cmd = ["gh", "issue", "edit", str(issue_number), "--repo", repo]
    if add:
        cmd += ["--add-label", add]
    if remove:
        cmd += ["--remove-label", remove]
    run(cmd, check=False)


def load_repos():
    """Load repos from config file or default."""
    if REPOS_FILE.exists():
        lines = REPOS_FILE.read_text().splitlines()
        repos = [
            line.strip() for line in lines if line.strip() and not line.strip().startswith("#")
        ]
        if repos:
            return repos
    return ["zachmayer/skills"]


def repo_dir(repo):
    """Map owner/repo to ~/source/repo-name."""
    return Path.home() / "source" / repo.split("/")[-1]


def branch_name(issue_number):
    """Canonical branch name for an issue."""
    return f"ai/issue-{issue_number}"


def worktree_path(repo, issue_number):
    """Worktree path for an issue."""
    repo_name = repo.split("/")[-1]
    return WORKTREE_BASE / repo_name / f"ai-issue-{issue_number}"


def log_path(repo, issue_number):
    """Log file path for an agent run."""
    repo_name = repo.split("/")[-1]
    return LOG_DIR / f"heartbeat-{repo_name}-{issue_number}.log"


def get_default_owner(repo):
    """Get the default CODEOWNERS owner (* rule) for a repo."""
    codeowners = repo_dir(repo) / ".github" / "CODEOWNERS"
    if codeowners.exists():
        for line in codeowners.read_text().splitlines():
            stripped = line.strip()
            if stripped.startswith("* ") and "@" in stripped:
                return stripped.split("@")[-1].strip()
    # Fallback: repo owner from org/repo format
    return repo.split("/")[0]


def gh_comment(repo, issue_number, body):
    """Post a comment on a GitHub issue."""
    body_file = SCRATCH_DIR / f"comment-{issue_number}.tmp"
    body_file.parent.mkdir(parents=True, exist_ok=True)
    body_file.write_text(body)
    run(
        [
            "gh",
            "issue",
            "comment",
            str(issue_number),
            "--repo",
            repo,
            "--body-file",
            str(body_file),
        ],
        check=False,
    )
    body_file.unlink(missing_ok=True)


def resolve_working_branch(all_prs, most_recent_open, canonical):
    """Determine the working branch: open PR's branch if one exists, else canonical."""
    if most_recent_open:
        open_pr = next((p for p in all_prs if p["number"] == most_recent_open), None)
        if open_pr:
            return open_pr["headRefName"]
    return canonical


# --- PR Discovery ---


PR_JSON_FIELDS = "number,state,title,headRefName"


def find_related_prs(repo, issue_number):
    """Find all PRs related to an issue. Returns (all_prs, most_recent_open_number)."""
    by_search = (
        gh_json(
            [
                "gh",
                "pr",
                "list",
                "--repo",
                repo,
                "--state",
                "all",
                "--search",
                f"#{issue_number}",
                "--json",
                PR_JSON_FIELDS,
                "--limit",
                "20",
            ]
        )
        or []
    )

    by_branch = (
        gh_json(
            [
                "gh",
                "pr",
                "list",
                "--repo",
                repo,
                "--state",
                "all",
                "--head",
                branch_name(issue_number),
                "--json",
                PR_JSON_FIELDS,
                "--limit",
                "5",
            ]
        )
        or []
    )

    seen = {pr["number"]: pr for pr in by_search + by_branch}
    all_prs = sorted(seen.values(), key=lambda p: p["number"])
    most_recent_open = max((p["number"] for p in all_prs if p["state"] == "OPEN"), default=None)
    return all_prs, most_recent_open


def build_related_prs_context(all_prs, most_recent_open, repo):
    """Format related PRs as context string for agent prompts."""
    if not all_prs:
        return "None"
    pr_nums = ", ".join(f"#{p['number']}" for p in all_prs)
    most_recent = max(p["number"] for p in all_prs)
    lines = [
        f"All: {pr_nums}",
        f"Most recent: #{most_recent}",
    ]
    if most_recent_open:
        lines.append(f"Most recent open: #{most_recent_open}")
    lines.append(f"Use `gh pr view <number> --repo {repo}` to review prior attempts.")
    lines.append(f"Use `gh pr diff <number> --repo {repo}` to see prior code changes.")
    if most_recent_open:
        lines.append("If there is a most recent open PR, you are working off that PR.")
    return "\n".join(lines)


# --- Core operations ---


def ensure_worktree(repo_path, branch, wt_path):
    """Reuse existing worktree or create new one.

    When reusing, fetches and resets to remote branch (switches if needed).
    """
    if wt_path.exists():
        run(["git", "fetch", "origin"], cwd=wt_path, check=False)
        # checkout -B handles both cases: switches branch or resets to remote
        run(["git", "checkout", "-B", branch, f"origin/{branch}"], cwd=wt_path, check=False)
        return
    wt_path.parent.mkdir(parents=True, exist_ok=True)
    run(["git", "worktree", "prune"], cwd=repo_path, check=False)
    # Delete stale local branch (safe: worktrees just pruned)
    run(["git", "branch", "-D", branch], cwd=repo_path, check=False)

    # Check if branch exists on remote
    remote_exists = run(
        ["git", "ls-remote", "--heads", "origin", f"refs/heads/{branch}"],
        cwd=repo_path,
        capture=True,
        check=False,
    ).stdout.strip()

    if remote_exists:
        run(
            ["git", "worktree", "add", "--track", "-b", branch, str(wt_path), f"origin/{branch}"],
            cwd=repo_path,
        )
    else:
        run(
            ["git", "worktree", "add", "-b", branch, str(wt_path), "origin/main"],
            cwd=repo_path,
        )


def ensure_branch_pushed(workdir, branch, issue_number):
    """Ensure branch is pushed to remote with at least one commit ahead of main."""
    if _rev_list_count(workdir, "origin/main..HEAD") == 0:
        run(
            ["git", "commit", "--allow-empty", "-m", f"ai: begin work on #{issue_number}"],
            cwd=workdir,
        )
    run(["git", "push", "-u", "origin", branch], cwd=workdir)


def ensure_pr(repo, issue, canonical_branch):
    """Create a draft PR on the canonical branch. Returns pr_number."""
    title = f"ai: resolve #{issue['number']} — {issue['title']}"
    body = f"Resolves #{issue['number']}\n\n*AI is working on this.*"
    body_file = SCRATCH_DIR / f"pr-body-{issue['number']}.tmp"
    body_file.parent.mkdir(parents=True, exist_ok=True)
    body_file.write_text(body)
    result = subprocess.run(
        [
            "gh",
            "pr",
            "create",
            "--repo",
            repo,
            "--head",
            canonical_branch,
            "--draft",
            "--title",
            title,
            "--body-file",
            str(body_file),
        ],
        capture_output=True,
        text=True,
    )
    body_file.unlink(missing_ok=True)
    if result.returncode != 0:
        raise RuntimeError(f"gh pr create failed: {result.stderr}")
    pr_url = result.stdout.strip()
    pr_number = int(pr_url.rstrip("/").split("/")[-1])
    return pr_number


def get_feedback(repo, issue_number, pr_number):
    """Get latest comments and reviews on issue/PR from all users."""
    comments = gh_json(["gh", "api", f"repos/{repo}/issues/{issue_number}/comments"]) or []
    if pr_number:
        comments += gh_json(["gh", "api", f"repos/{repo}/issues/{pr_number}/comments"]) or []
        reviews = gh_json(["gh", "api", f"repos/{repo}/pulls/{pr_number}/reviews"]) or []
        for r in reviews:
            if r.get("body"):
                comments.append(r)
    with_body = [c for c in comments if c.get("body")]
    if not with_body:
        return "None"
    with_body.sort(key=lambda c: c.get("created_at", c.get("submitted_at", "")), reverse=True)
    return "\n\n".join(
        f"[{c.get('user', {}).get('login', '?')}] {c['body']}" for c in with_body[:5]
    )


def get_ci_status(repo, pr_number):
    """Get CI status for a PR."""
    if not pr_number:
        return "No PR yet"
    data = gh_json(
        [
            "gh",
            "pr",
            "view",
            str(pr_number),
            "--repo",
            repo,
            "--json",
            "statusCheckRollup",
        ]
    )
    if not data:
        return "No CI runs yet"
    rollup = data.get("statusCheckRollup") or []
    if not rollup:
        return "No CI runs yet"
    failing = [c for c in rollup if c.get("conclusion") == "FAILURE"]
    if not failing:
        return "All passing"
    return "Failing: " + ", ".join(c.get("name", "?") for c in failing)


def _rev_list_count(workdir, spec):
    """Count commits in a rev-list spec (e.g. 'origin/main..HEAD')."""
    result = run(["git", "rev-list", "--count", spec], cwd=workdir, capture=True, check=False)
    try:
        return int(result.stdout.strip())
    except ValueError:
        return 0


def is_behind_main(workdir):
    """Check if branch is behind origin/main. Caller must fetch first."""
    return _rev_list_count(workdir, "HEAD..origin/main") > 0


def has_diff(workdir):
    """Check if the branch has file changes that are unique to this branch (vs merge-base)."""
    result = run(
        ["git", "diff", "--stat", "origin/main...HEAD"], cwd=workdir, capture=True, check=False
    )
    return bool(result.stdout.strip())


def run_verification(workdir):
    """Run make test + make lint. Returns list of failure names (empty = all passed)."""
    test_result = run(["make", "test"], cwd=workdir, capture=True, check=False)
    lint_result = run(["make", "lint"], cwd=workdir, capture=True, check=False)
    failures = []
    if test_result.returncode != 0:
        failures.append("tests")
    if lint_result.returncode != 0:
        failures.append("lint")
    return failures


# --- Agent invocation ---


def build_context(
    agent_name,
    *,
    issue_number,
    repo,
    issue_title,
    issue_body,
    pr_number=None,
    branch=None,
    related_prs="None",
    feedback="None",
    ci_status="No CI runs yet",
    branch_status="Up to date with main",
):
    """Build agent prompt by substituting variables in the agent template."""
    agent_file = AGENT_DIR / f"{agent_name}.md"
    template_text = agent_file.read_text()

    # Strip YAML frontmatter (between --- markers)
    if template_text.startswith("---"):
        end = template_text.index("---", 3)
        template_text = template_text[end + 3 :].lstrip("\n")

    tmpl = string.Template(template_text)
    return tmpl.safe_substitute(
        ISSUE_NUMBER=issue_number,
        REPO=repo,
        ISSUE_TITLE=issue_title,
        ISSUE_BODY=issue_body or "",
        PR_NUMBER=pr_number or "",
        BRANCH=branch or "",
        RELATED_PRS=related_prs,
        FEEDBACK=feedback,
        CI_STATUS=ci_status,
        BRANCH_STATUS=branch_status,
        RESULT_FILE=str(SCRATCH_DIR / f"queue-result-{issue_number}.txt"),
    )


def invoke_agent(agent_name, workdir, context, issue_number, repo, *, budget=8):
    """Invoke a named Claude agent. Agent must be installed in ~/.claude/agents/."""
    lf = log_path(repo, issue_number)
    log.info(f"Invoking agent '{agent_name}', log: {lf}")

    cmd = [
        "claude",
        "--agent",
        agent_name,
        "--print",
        "--model",
        "opus",
        "--effort",
        "max",
        # Agents run non-interactively (--print) and can't get user approval
        # for file writes. They operate in isolated worktrees with a limited
        # OAuth token (no repo admin, no org access).
        "--dangerously-skip-permissions",
        "--max-budget-usd",
        str(budget),
        "--add-dir",
        str(OBSIDIAN_DIR),
        "-p",
        context,
    ]
    # Strip CLAUDECODE env var so child agents don't think they're nested
    env = {k: v for k, v in os.environ.items() if k != "CLAUDECODE"}

    # Append so queue→coding→review logs accumulate in one file
    with open(lf, "a") as f:
        f.write(f"\n{'=' * 60}\n[{agent_name}] agent invocation\n{'=' * 60}\n")
        result = subprocess.run(cmd, cwd=workdir, stdout=f, stderr=subprocess.STDOUT, env=env)
        f.write(f"\n[{agent_name}] exit code: {result.returncode}\n")
    return result.returncode


# --- Pipeline phases ---


def remove_ai_labels(repo, issue_number):
    """Remove all ai: labels from an issue."""
    set_label(repo, issue_number, remove="ai:coding,ai:queued,ai:review")


def process_queue(repo, repo_path, issue):
    """Phase 1: Scope a queued issue.

    Runs the queue agent in the repo dir (no worktree/PR needed yet).
    The agent posts a plan or questions as an issue comment.
    Exit 0 = actionable → ai:coding. Exit 2 = needs clarification → human.
    """
    num = issue["number"]

    log.info(f"[queue] Processing {repo}#{num}: {issue['title']}")

    all_prs, most_recent_open = find_related_prs(repo, num)
    related_ctx = build_related_prs_context(all_prs, most_recent_open, repo)

    context = build_context(
        "queue",
        issue_number=num,
        repo=repo,
        issue_title=issue["title"],
        issue_body=issue.get("body") or "",
        related_prs=related_ctx,
    )

    # Run queue agent in the main repo dir — no worktree needed for scoping
    result_file = SCRATCH_DIR / f"queue-result-{num}.txt"
    result_file.unlink(missing_ok=True)
    exit_code = invoke_agent("queue", repo_path, context, num, repo, budget=10)

    if exit_code != 0:
        remove_ai_labels(repo, num)
        gh_comment(repo, num, f"Queue agent crashed (exit {exit_code}). Log: {log_path(repo, num)}")
        return

    # Read agent's determination from sentinel file
    determination = result_file.read_text().strip() if result_file.exists() else "actionable"
    result_file.unlink(missing_ok=True)

    if determination == "blocked":
        remove_ai_labels(repo, num)
        log.info(f"[queue] {repo}#{num}: needs clarification, returned to human")
        return

    # Transition to coding — the coding phase creates worktree/PR as needed
    set_label(repo, num, "ai:coding", remove="ai:queued")
    log.info(f"[queue] Done {repo}#{num}, moving to coding")


def process_coding(repo, repo_path, issue):
    """Phase 2: Write code for a coding issue."""
    num = issue["number"]
    canonical = branch_name(num)
    wt = worktree_path(repo, num)

    log.info(f"[coding] Processing {repo}#{num}: {issue['title']}")
    run(["git", "fetch", "origin"], cwd=repo_path, check=False)

    all_prs, most_recent_open = find_related_prs(repo, num)
    related_ctx = build_related_prs_context(all_prs, most_recent_open, repo)

    # Determine the working branch before creating worktree
    working_branch = resolve_working_branch(all_prs, most_recent_open, canonical)

    # Ensure worktree on the correct branch
    ensure_worktree(repo_path, working_branch, wt)

    # Ensure PR exists
    pr_number = most_recent_open
    if not pr_number:
        ensure_branch_pushed(wt, canonical, num)
        pr_number = ensure_pr(repo, issue, canonical)

    context = build_context(
        "coding",
        issue_number=num,
        repo=repo,
        issue_title=issue["title"],
        issue_body=issue.get("body") or "",
        pr_number=pr_number,
        branch=working_branch,
        related_prs=related_ctx,
        feedback=get_feedback(repo, num, pr_number),
        ci_status=get_ci_status(repo, pr_number),
        branch_status=(
            "Behind main — merge needed" if is_behind_main(wt) else "Up to date with main"
        ),
    )

    exit_code = invoke_agent("coding", wt, context, num, repo, budget=25)

    if exit_code != 0:
        remove_ai_labels(repo, num)
        gh_comment(
            repo, num, f"Coding agent crashed (exit {exit_code}). Log: {log_path(repo, num)}"
        )
        return

    # Check if agent produced actual file changes
    if not has_diff(wt):
        log.info(f"[coding] {repo}#{num}: no diff, bailing")
        gh_comment(
            repo, num, "Coding agent completed but produced no changes. Removing from pipeline."
        )
        remove_ai_labels(repo, num)
        return

    # Post-build verification
    failures = run_verification(wt)
    if failures:
        gh_comment(
            repo,
            num,
            f"Post-build verification failed: {', '.join(failures)}. Fix and push again.",
        )
        # Stay in ai:coding for next heartbeat
        log.info(f"[coding] {repo}#{num}: verification failed ({', '.join(failures)})")
        return

    # Verification passed — move to review
    set_label(repo, num, "ai:review", remove="ai:coding")
    log.info(f"[coding] Done {repo}#{num}, moving to review")


def process_review(repo, repo_path, issue):
    """Phase 3: Review a PR for a review issue.

    The review agent leaves a comment via gh pr review --comment.
    GitHub blocks self-approval (PR author == reviewer), so we use comments.
    After review, always assign to human and mark ready.
    """
    num = issue["number"]
    wt = worktree_path(repo, num)

    log.info(f"[review] Processing {repo}#{num}: {issue['title']}")
    run(["git", "fetch", "origin"], cwd=repo_path, check=False)

    all_prs, most_recent_open = find_related_prs(repo, num)
    if not most_recent_open:
        log.warning(f"[review] {repo}#{num}: no open PR found, removing labels")
        remove_ai_labels(repo, num)
        return

    pr_number = most_recent_open

    # Determine working branch for worktree
    working_branch = resolve_working_branch(all_prs, most_recent_open, branch_name(num))

    # Ensure worktree exists on the correct branch and run verification
    ensure_worktree(repo_path, working_branch, wt)
    failures = run_verification(wt)
    if failures:
        log.info(f"[review] {repo}#{num}: pre-review verification failed ({', '.join(failures)})")
        set_label(repo, num, "ai:coding", remove="ai:review")
        return

    context = build_context(
        "review",
        issue_number=num,
        repo=repo,
        issue_title=issue["title"],
        issue_body=issue.get("body") or "",
        pr_number=pr_number,
    )

    exit_code = invoke_agent("review", wt, context, num, repo, budget=10)

    if exit_code != 0:
        remove_ai_labels(repo, num)
        gh_comment(
            repo, num, f"Review agent crashed (exit {exit_code}). Log: {log_path(repo, num)}"
        )
        return

    # Review agent leaves a comment. Always assign to human and mark ready.
    # GitHub blocks self-approval, so we can't use gh pr review --approve.
    owner = get_default_owner(repo)
    run(
        ["gh", "pr", "edit", str(pr_number), "--repo", repo, "--add-assignee", owner],
        check=False,
    )
    run(["gh", "pr", "ready", str(pr_number), "--repo", repo], check=False)
    remove_ai_labels(repo, num)
    log.info(f"[review] {repo}#{num}: reviewed, assigned to {owner}")


# --- Sweep ---


def sweep_stale_issues(repo):
    """Remove ai: labels from issues whose PRs were merged/closed by human.

    Only strips labels when PRs existed but none are open — avoids race
    with newly-labeled issues that don't have PRs yet.
    """
    for label in ["ai:coding", "ai:review"]:
        for issue in get_labeled_issues(repo, label):
            num = issue["number"]
            all_prs, most_recent_open = find_related_prs(repo, num)
            if all_prs and not most_recent_open:
                log.info(f"[sweep] {repo}#{num}: PRs closed/merged, removing labels")
                remove_ai_labels(repo, num)


def get_labeled_issues(repo, label):
    """Get open issues with a given label."""
    return (
        gh_json(
            [
                "gh",
                "issue",
                "list",
                "--repo",
                repo,
                "--label",
                label,
                "--state",
                "open",
                "--json",
                "number,title,body",
                "--limit",
                "25",
            ]
        )
        or []
    )


# --- Main loop ---


@click.command()
@click.option("--dry-run", is_flag=True, help="Show what would be processed")
def main(dry_run):
    """Process GitHub issues through the three-phase pipeline.

    Issues flow: ai:queued → ai:coding → ai:review → human.
    Each phase can progress in a single heartbeat cycle.
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [heartbeat] %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%SZ",
    )

    lock_fd = open(LOCK_FILE, "w")
    try:
        fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        lock_fd.close()
        log.info("Another heartbeat is running, exiting")
        return

    try:
        for repo in load_repos():
            rp = repo_dir(repo)
            if not (rp / ".git").exists():
                log.info(f"Skipping {repo} — {rp} not a git repo")
                continue

            sweep_stale_issues(repo)

            # Loop 1: Queue (scope queued issues)
            queued = get_labeled_issues(repo, "ai:queued")
            for issue in queued[:MAX_ISSUES]:
                if dry_run:
                    log.info(f"[dry-run] Would queue {repo}#{issue['number']}: {issue['title']}")
                    continue
                try:
                    process_queue(repo, rp, issue)
                except Exception:
                    log.exception(f"Failed to process queue {repo}#{issue['number']}")

            # Loop 2: Coding (write code for coding issues)
            # Re-queries GitHub so issues just promoted from queue are included.
            coding = get_labeled_issues(repo, "ai:coding")
            for issue in coding[:MAX_ISSUES]:
                if dry_run:
                    log.info(f"[dry-run] Would code {repo}#{issue['number']}: {issue['title']}")
                    continue
                try:
                    process_coding(repo, rp, issue)
                except Exception:
                    log.exception(f"Failed to process coding {repo}#{issue['number']}")

            # Loop 3: Review (review PRs for review issues)
            review = get_labeled_issues(repo, "ai:review")
            for issue in review[:MAX_ISSUES]:
                if dry_run:
                    log.info(f"[dry-run] Would review {repo}#{issue['number']}: {issue['title']}")
                    continue
                try:
                    process_review(repo, rp, issue)
                except Exception:
                    log.exception(f"Failed to process review {repo}#{issue['number']}")
    finally:
        fcntl.flock(lock_fd, fcntl.LOCK_UN)
        lock_fd.close()


if __name__ == "__main__":
    main()
