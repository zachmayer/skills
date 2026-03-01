#!/usr/bin/env python3
"""Heartbeat orchestrator: find issues, prepare worktrees/PRs, invoke Claude Code."""

import fcntl
import json
import logging
import os
import string
import subprocess
from pathlib import Path

import click

MAX_ISSUES = 10
STALE_HOURS = 4
LOCK_FILE = Path.home() / ".claude" / "heartbeat.lock"
REPOS_FILE = Path.home() / ".claude" / "heartbeat-repos.conf"
OBSIDIAN_DIR = Path(os.environ.get("CLAUDE_OBSIDIAN_DIR", "~/claude/obsidian")).expanduser()
WORKTREE_BASE = Path.home() / "claude" / "worktrees"
SCRATCH_DIR = Path.home() / "claude" / "scratch"
LOG_DIR = Path.home() / ".claude"
SCRIPT_DIR = Path(__file__).parent
ISSUE_AUTHOR = os.environ.get("HEARTBEAT_ISSUE_AUTHOR", "zachmayer")

log = logging.getLogger("heartbeat")


# --- Helpers ---


def run(cmd, *, cwd=None, capture=False, check=True):
    """Run a command. String uses shell; list uses direct exec."""
    result = subprocess.run(
        cmd,
        shell=isinstance(cmd, str),
        cwd=cwd,
        capture_output=capture,
        text=True,
    )
    if check and result.returncode != 0:
        raise subprocess.CalledProcessError(result.returncode, cmd, result.stdout, result.stderr)
    return result


def gh_json(cmd):
    """Run a gh command and parse JSON output. Returns parsed JSON or None."""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0 or not result.stdout.strip():
        return None
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return None


def set_label(repo, issue_number, add, *, remove=None):
    """Set labels on an issue. remove can be a string or comma-separated list."""
    cmd = f"gh issue edit {issue_number} --repo {repo} --add-label {add}"
    if remove:
        cmd += f" --remove-label {remove}"
    run(cmd, check=False)


def log_path(repo, issue_number):
    """Log file path, namespaced by repo to avoid collisions."""
    repo_name = repo.split("/")[-1]
    return LOG_DIR / f"heartbeat-{repo_name}-{issue_number}.log"


def get_labels(repo, issue_number):
    """Get current labels on an issue."""
    data = gh_json(f"gh issue view {issue_number} --repo {repo} --json labels")
    if not data:
        return set()
    return {label["name"] for label in data.get("labels", [])}


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


# --- Core operations ---


def ensure_worktree(repo_path, branch, wt_path):
    """Reuse existing worktree or create new one."""
    if wt_path.exists():
        # Clean up any artifacts from crashed agent runs
        run("git checkout -- .", cwd=wt_path, check=False)
        run("git clean -fdx", cwd=wt_path, check=False)
        result = run("git pull --rebase=false", cwd=wt_path, capture=True, check=False)
        if result.returncode != 0:
            # Merge conflict or corrupted state — nuke and recreate
            log.warning(f"Pull failed in {wt_path}, recreating worktree")
            import shutil

            run(f"git worktree remove --force {wt_path}", cwd=repo_path, check=False)
            shutil.rmtree(wt_path, ignore_errors=True)
            # Fall through to creation below
        else:
            return
    wt_path.parent.mkdir(parents=True, exist_ok=True)
    run("git worktree prune", cwd=repo_path, check=False)
    # Delete stale local branch (safe: worktrees just pruned)
    run(f"git branch -D {branch}", cwd=repo_path, check=False)

    # Check if branch exists on remote
    remote_exists = run(
        f"git ls-remote --heads origin refs/heads/{branch}",
        cwd=repo_path,
        capture=True,
        check=False,
    ).stdout.strip()

    if remote_exists:
        run(
            f"git worktree add --track -b {branch} {wt_path} origin/{branch}",
            cwd=repo_path,
        )
    else:
        run(f"git worktree add -b {branch} {wt_path} origin/main", cwd=repo_path)


def ensure_branch_pushed(workdir, branch, issue_number):
    """Ensure branch is pushed to remote with at least one commit ahead of main."""
    remote_exists = run(
        f"git ls-remote --heads origin refs/heads/{branch}",
        cwd=workdir,
        capture=True,
        check=False,
    ).stdout.strip()
    if remote_exists:
        return

    # Check if ahead of main
    result = run(
        "git rev-list --count origin/main..HEAD",
        cwd=workdir,
        capture=True,
        check=False,
    )
    try:
        ahead = int(result.stdout.strip())
    except ValueError:
        ahead = 0

    if ahead == 0:
        run(
            f'git commit --allow-empty -m "ai: begin work on #{issue_number}"',
            cwd=workdir,
        )
    run(f"git push -u origin {branch}", cwd=workdir)


def ensure_pr(repo, issue, branch):
    """Ensure exactly one open PR from the canonical branch. Returns PR number."""
    prs = gh_json(f"gh pr list --repo {repo} --head {branch} --state open --json number")
    if prs:
        pr_number = prs[0]["number"]
    else:
        title = f"ai: resolve #{issue['number']} — {issue['title']}"
        body = f"Resolves #{issue['number']}\n\n*AI is working on this.*"
        body_file = SCRATCH_DIR / "pr-body.tmp"
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
                branch,
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

    # Cleanup non-canonical open PRs linked to this issue
    cleanup_linked_prs(repo, issue["number"], pr_number)
    return pr_number


def cleanup_linked_prs(repo, issue_number, canonical_pr):
    """Close non-canonical open PRs linked to an issue via GraphQL."""
    owner, name = repo.split("/")
    query = (
        "query($owner: String!, $name: String!, $number: Int!) {"
        "  repository(owner: $owner, name: $name) {"
        "    issue(number: $number) {"
        "      closedByPullRequestsReferences(first: 20) {"
        "        nodes { number state }"
        "      }"
        "    }"
        "  }"
        "}"
    )
    result = subprocess.run(
        [
            "gh",
            "api",
            "graphql",
            "-f",
            f"query={query}",
            "-F",
            f"owner={owner}",
            "-F",
            f"name={name}",
            "-F",
            f"number={issue_number}",
        ],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return
    try:
        nodes = json.loads(result.stdout)["data"]["repository"]["issue"][
            "closedByPullRequestsReferences"
        ]["nodes"]
        for pr in nodes:
            if pr["number"] != canonical_pr and pr.get("state") == "OPEN":
                run(
                    f"gh pr close {pr['number']} --repo {repo} "
                    f'--comment "Work continuing on #{canonical_pr}"',
                    check=False,
                )
    except (json.JSONDecodeError, KeyError, TypeError):
        pass


def get_human_feedback(repo, issue_number, pr_number):
    """Get latest comments from the authorized user on issue/PR."""
    comments = gh_json(f"gh api repos/{repo}/issues/{issue_number}/comments") or []
    if pr_number:
        comments += gh_json(f"gh api repos/{repo}/issues/{pr_number}/comments") or []
        reviews = gh_json(f"gh api repos/{repo}/pulls/{pr_number}/reviews") or []
        for r in reviews:
            if r.get("body") and r.get("user", {}).get("login") == ISSUE_AUTHOR:
                comments.append(r)
        # Inline code review comments (on specific lines)
        review_comments = gh_json(f"gh api repos/{repo}/pulls/{pr_number}/comments") or []
        for c in review_comments:
            if c.get("user", {}).get("login") == ISSUE_AUTHOR and c.get("body"):
                path = c.get("path", "")
                body = f"[{path}] {c['body']}" if path else c["body"]
                comments.append({**c, "body": body})
    owner_comments = [
        c for c in comments if c.get("user", {}).get("login") == ISSUE_AUTHOR and c.get("body")
    ]
    if not owner_comments:
        return "None"
    owner_comments.sort(key=lambda c: c.get("created_at", c.get("submitted_at", "")), reverse=True)
    return "\n\n".join(c["body"] for c in owner_comments[:5])


def get_ci_status(repo, pr_number):
    """Get CI status for a PR."""
    if not pr_number:
        return "No PR yet"
    data = gh_json(f"gh pr view {pr_number} --repo {repo} --json statusCheckRollup")
    if not data:
        return "No CI runs yet"
    rollup = data.get("statusCheckRollup") or []
    if not rollup:
        return "No CI runs yet"
    failing = [c for c in rollup if c.get("conclusion") == "FAILURE"]
    if not failing:
        return "All passing"
    return "Failing: " + ", ".join(c.get("name", "?") for c in failing)


def get_prior_prs(repo, issue_number, current_pr):
    """Get closed/merged PRs and old open PRs related to this issue."""
    prs = (
        gh_json(
            f"gh pr list --repo {repo} --state all "
            f'--search "issue-{issue_number}" '
            f"--json number,title,state,body --limit 10"
        )
        or []
    )
    prior = [p for p in prs if p["number"] != current_pr]
    if not prior:
        return "None"
    return "\n".join(
        f"#{p['number']} ({p['state']}): {p['title']} — {(p.get('body') or '')[:200]}"
        for p in prior
    )


def is_behind_main(workdir):
    """Check if branch is behind origin/main."""
    run("git fetch origin main", cwd=workdir, check=False)
    result = run(
        "git rev-list --count HEAD..origin/main",
        cwd=workdir,
        capture=True,
        check=False,
    )
    try:
        return int(result.stdout.strip()) > 0
    except ValueError:
        return False


def build_prompt(
    *,
    issue_number,
    repo,
    issue_title,
    issue_body,
    pr_number,
    branch,
    prior_prs,
    human_feedback,
    ci_status,
    branch_status,
):
    """Build agent prompt from worker_prompt.md template."""
    template_text = (SCRIPT_DIR / "worker_prompt.md").read_text()
    tmpl = string.Template(template_text)
    return tmpl.safe_substitute(
        ISSUE_NUMBER=issue_number,
        REPO=repo,
        ISSUE_TITLE=issue_title,
        ISSUE_BODY=issue_body,
        PR_NUMBER=pr_number,
        BRANCH=branch,
        PRIOR_PRS=prior_prs,
        HUMAN_FEEDBACK=human_feedback,
        CI_STATUS=ci_status,
        BRANCH_STATUS=branch_status,
    )


def invoke_agent(workdir, prompt, issue_number, repo):
    """Invoke Claude Code agent. Returns exit code."""
    log_file = log_path(repo, issue_number)
    log.info(f"Invoking agent, log: {log_file}")
    with open(log_file, "w") as lf:
        result = subprocess.run(
            [
                "claude",
                "--print",
                "--permission-mode",
                "dontAsk",
                "--model",
                "opus",
                "--max-turns",
                "100",
                "--max-budget-usd",
                "8",
                "--add-dir",
                str(OBSIDIAN_DIR),
                "-p",
                prompt,
            ],
            cwd=workdir,
            stdout=lf,
            stderr=subprocess.STDOUT,
        )
    return result.returncode


# --- Main loop ---


def sweep_draft_prs(repo):
    """Mark draft PRs ready if CI has passed (handles CI timing gap)."""
    drafts = gh_json(
        f"gh pr list --repo {repo} --draft --label ai:human "
        f"--json number,statusCheckRollup,changedFiles --limit 25"
    )
    if not drafts:
        return
    for pr in drafts:
        if pr.get("changedFiles", 0) == 0:
            continue
        rollup = pr.get("statusCheckRollup") or []
        if not rollup:
            continue
        ci_ok = not any(c.get("conclusion") == "FAILURE" for c in rollup)
        pending = any(c.get("status") == "IN_PROGRESS" for c in rollup)
        if ci_ok and not pending:
            log.info(f"Marking {repo}#{pr['number']} ready (CI passed)")
            run(f"gh pr ready {pr['number']} --repo {repo}", check=False)


def sweep_stale_issues(repo):
    """Move issues stuck in ai:coding for too long to ai:human."""
    stale = gh_json(
        f"gh issue list --repo {repo} --label ai:coding "
        f"--state open --json number,updatedAt --limit 25"
    )
    if not stale:
        return
    from datetime import datetime
    from datetime import timezone

    cutoff = datetime.now(timezone.utc).timestamp() - (STALE_HOURS * 3600)
    for issue in stale:
        updated = issue.get("updatedAt", "")
        if not updated:
            continue
        try:
            ts = datetime.fromisoformat(updated.replace("Z", "+00:00")).timestamp()
        except ValueError:
            continue
        if ts < cutoff:
            log.info(f"Sweeping stale {repo}#{issue['number']} (stuck in ai:coding)")
            run(
                f"gh issue comment {issue['number']} --repo {repo} "
                f'--body "Stale ai:coding label (>{STALE_HOURS}h). Moving to ai:human."',
                check=False,
            )
            set_label(repo, issue["number"], "ai:human", remove="ai:coding")


def process_issue(repo, repo_path, issue):
    """Process a single issue: worktree -> PR -> prompt -> agent -> safety net."""
    num = issue["number"]
    branch = branch_name(num)
    wt = worktree_path(repo, num)

    log.info(f"Processing {repo}#{num}: {issue['title']}")
    run("git fetch origin", cwd=repo_path, check=False)
    ensure_worktree(repo_path, branch, wt)
    ensure_branch_pushed(wt, branch, num)
    pr_number = ensure_pr(repo, issue, branch)

    prompt = build_prompt(
        issue_number=num,
        repo=repo,
        issue_title=issue["title"],
        issue_body=issue.get("body") or "",
        pr_number=pr_number,
        branch=branch,
        prior_prs=get_prior_prs(repo, num, pr_number),
        human_feedback=get_human_feedback(repo, num, pr_number),
        ci_status=get_ci_status(repo, pr_number),
        branch_status=(
            "Behind main — merge needed" if is_behind_main(wt) else "Up to date with main"
        ),
    )

    # Claim: set ai:coding, remove both ai:queued and ai:human
    set_label(repo, num, "ai:coding", remove="ai:queued,ai:human")
    exit_code = invoke_agent(wt, prompt, num, repo)

    # Safety net: always post log on failure, regardless of label state
    if exit_code != 0:
        lf = log_path(repo, num)
        run(
            f"gh issue comment {num} --repo {repo} "
            f'--body "Agent exited with code {exit_code}. Log: {lf}"',
            check=False,
        )
        set_label(repo, num, "ai:human", remove="ai:coding,ai:queued")

    log.info(f"Done {repo}#{num}, exit={exit_code}")


@click.command()
@click.option("--dry-run", is_flag=True, help="Show what would be processed")
def main(dry_run):
    """Process GitHub issues labeled ai:queued or ai:coding."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [heartbeat] %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%SZ",
    )

    LOG_DIR.mkdir(parents=True, exist_ok=True)
    lock_fd = open(LOCK_FILE, "w")
    try:
        fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        log.info("Another heartbeat is running, exiting")
        return

    try:
        for repo in load_repos():
            rp = repo_dir(repo)
            if not (rp / ".git").exists():
                log.info(f"Skipping {repo} — {rp} not a git repo")
                continue

            # Sweep stale ai:coding issues and stuck draft PRs
            sweep_stale_issues(repo)
            sweep_draft_prs(repo)

            issues = (
                gh_json(
                    f"gh issue list --repo {repo} --label ai:queued "
                    f"--state open --json number,title,body --limit 25"
                )
                or []
            )
            issues += (
                gh_json(
                    f"gh issue list --repo {repo} --label ai:coding "
                    f"--state open --json number,title,body --limit 25"
                )
                or []
            )

            # Deduplicate
            seen = set()
            unique = []
            for issue in issues:
                if issue["number"] not in seen:
                    seen.add(issue["number"])
                    unique.append(issue)

            for issue in unique[:MAX_ISSUES]:
                if dry_run:
                    log.info(f"[dry-run] Would process {repo}#{issue['number']}: {issue['title']}")
                    continue
                try:
                    process_issue(repo, rp, issue)
                except Exception:
                    log.exception(f"Failed to process {repo}#{issue['number']}")
                    # Prevent infinite retry: move to ai:human so it doesn't loop
                    run(
                        f"gh issue comment {issue['number']} --repo {repo} "
                        f'--body "Orchestrator error — moved to ai:human for triage."',
                        check=False,
                    )
                    set_label(repo, issue["number"], "ai:human", remove="ai:queued,ai:coding")
    finally:
        fcntl.flock(lock_fd, fcntl.LOCK_UN)
        lock_fd.close()


if __name__ == "__main__":
    main()
