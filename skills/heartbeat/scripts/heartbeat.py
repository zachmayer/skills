"""Heartbeat: Two-agent FSM (lead + dev) driven by status labels.

Step 1: Lead agent processes all status:lead issues (route, scope, review).
Step 2: Dev agent processes all status:dev issues (build, push, hand back).
"""

import json
import os
import random
import shutil
import subprocess
import tempfile
from datetime import datetime
from datetime import timezone
from pathlib import Path

import click

STATUS_FILE = Path.home() / ".claude" / "heartbeat.status"
REPOS_FILE = Path.home() / ".claude" / "heartbeat-repos.conf"
DEFAULT_REPO = "zachmayer/skills"


def ts() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def log(msg: str) -> None:
    click.echo(f"[{ts()}] {msg}")


def repo_dir(repo: str) -> Path:
    return Path.home() / "source" / repo.split("/")[-1]


def load_repos() -> list[str]:
    if REPOS_FILE.exists():
        lines = REPOS_FILE.read_text().splitlines()
        repos = [ln.strip() for ln in lines if ln.strip() and not ln.strip().startswith("#")]
        if repos:
            return repos
    return [DEFAULT_REPO]


def collect_issues(repos: list[str], label: str, max_issues: int) -> list[dict]:
    """Collect labeled issues across repos via gh CLI."""
    shuffled = repos[:]
    random.shuffle(shuffled)
    all_issues: list[dict] = []

    for repo in shuffled:
        rdir = repo_dir(repo)
        if not (rdir / ".git").is_dir():
            log(f"Skipping {repo} — {rdir} not a git repo")
            continue

        if (
            subprocess.run(
                ["git", "-C", str(rdir), "fetch", "origin"], capture_output=True
            ).returncode
            != 0
        ):
            log(f"Skipping {repo} — fetch failed")
            continue

        result = subprocess.run(
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
            ],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            continue

        for issue in json.loads(result.stdout or "[]"):
            issue["repo"] = repo
            all_issues.append(issue)

    return all_issues[:max_issues]


def build_prompt(repo: str, number: int, issue: dict, auth_user: str, obsidian_dir: str) -> str:
    title = issue.get("title") or ""
    body = issue.get("body") or ""
    return (
        f"<issue>\nRepo: {repo}\nIssue: #{number}\nTitle: {title}\n"
        f"Authorized user: {auth_user}\nObsidian dir: {obsidian_dir}\n"
        f"Current time: {ts()}\n\n{body}\n</issue>"
    )


def run_agent(
    agent: str,
    repo: str,
    number: int,
    issue: dict,
    budget: int,
    max_turns: int,
    auth_user: str,
    obsidian_dir: str,
) -> bool:
    """Run a claude agent on a single issue. Returns True on success."""
    rdir = repo_dir(repo)
    # Fall back to repo owner if no explicit auth user
    effective_auth = auth_user or repo.split("/")[0]
    log(f"Running {agent} on {repo}#{number} (budget: ${budget})")

    prompt = build_prompt(repo, number, issue, effective_auth, obsidian_dir)
    workdir = None
    run_dir = rdir

    if agent == "dev":
        workdir = Path(tempfile.mkdtemp(prefix=f"heartbeat-{number}-"))
        subprocess.run(["git", "-C", str(rdir), "worktree", "prune"], capture_output=True)
        result = subprocess.run(
            ["git", "-C", str(rdir), "worktree", "add", "--detach", str(workdir), "origin/main"],
            capture_output=True,
        )
        if result.returncode != 0:
            log(f"Failed to create worktree for {repo}#{number}")
            shutil.rmtree(workdir, ignore_errors=True)
            return False
        run_dir = workdir

    try:
        result = subprocess.run(
            [
                "claude",
                "--print",
                "--agent",
                agent,
                "--add-dir",
                obsidian_dir,
                "--max-turns",
                str(max_turns),
                "--max-budget-usd",
                str(budget),
                prompt,
            ],
            cwd=str(run_dir),
            capture_output=True,
            text=True,
        )
        ok = result.returncode == 0
        if result.stdout.strip():
            log(f"{agent} output:\n{result.stdout.strip()}")
        if result.stderr.strip():
            log(f"{agent} stderr:\n{result.stderr.strip()}")
    except Exception as exc:
        log(f"{agent} on {repo}#{number} error: {exc!r}")
        ok = False

    if not ok:
        log(
            f"{agent} on {repo}#{number} failed (exit {result.returncode if 'result' in dir() else '?'})"
        )

    if workdir and workdir.is_dir():
        subprocess.run(
            ["git", "-C", str(rdir), "worktree", "remove", str(workdir), "--force"],
            capture_output=True,
        )

    return ok


def process_step(
    label: str,
    agent: str,
    repos: list[str],
    budget: int,
    max_turns: int,
    max_issues: int,
    auth_user: str,
    obsidian_dir: str,
) -> tuple[int, int]:
    """Run agent on all issues with label. Returns (total, succeeded)."""
    log(f"Querying {label} issues...")
    issues = collect_issues(repos, label, max_issues)

    if not issues:
        log(f"No {label} issues found")
        return 0, 0

    log(f"Found {len(issues)} {label} issues")
    ok = 0
    for issue in issues:
        repo, number = issue["repo"], issue["number"]
        if run_agent(agent, repo, number, issue, budget, max_turns, auth_user, obsidian_dir):
            ok += 1

    return len(issues), ok


@click.command()
@click.option("--lead-budget", default=3, help="$/issue for lead agent")
@click.option("--dev-budget", default=8, help="$/issue for dev agent")
@click.option("--lead-turns", default=50, help="Max turns for lead agent")
@click.option("--dev-turns", default=100, help="Max turns for dev agent")
@click.option("--max-issues", default=10, help="Max issues per step")
def main(
    lead_budget: int,
    dev_budget: int,
    lead_turns: int,
    dev_turns: int,
    max_issues: int,
) -> None:
    obsidian_dir = str(
        Path(os.environ.get("CLAUDE_OBSIDIAN_DIR", "~/claude/obsidian")).expanduser()
    )
    auth_user = os.environ.get("HEARTBEAT_AUTH_USER", "")

    repos = load_repos()
    log("Heartbeat round starting")

    lead_total, lead_ok = process_step(
        "status:lead",
        "lead",
        repos,
        lead_budget,
        lead_turns,
        max_issues,
        auth_user,
        obsidian_dir,
    )
    dev_total, dev_ok = process_step(
        "status:dev",
        "dev",
        repos,
        dev_budget,
        dev_turns,
        max_issues,
        auth_user,
        obsidian_dir,
    )

    # Record outcome
    STATUS_FILE.parent.mkdir(parents=True, exist_ok=True)
    if lead_total == 0 and dev_total == 0:
        STATUS_FILE.write_text(f"{ts()} IDLE\n")
        log("No issues to process")
    else:
        status = "OK" if lead_ok == lead_total and dev_ok == dev_total else "PARTIAL"
        line = f"{ts()} {status} lead={lead_ok}/{lead_total} dev={dev_ok}/{dev_total}"
        STATUS_FILE.write_text(line + "\n")
        log(f"Round complete ({status}): lead={lead_ok}/{lead_total} dev={dev_ok}/{dev_total}")


if __name__ == "__main__":
    main()
