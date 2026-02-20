#!/bin/bash
# select_prs.sh - Discover actionable PRs for heartbeat agent
#
# Three-tier priority:
#   Tier 1: PRs where authorized user left feedback after latest commit
#   Tier 2: PRs with no review feedback at all
#   Tier 3: No actionable PRs (caller falls back to issues)
#
# Security: Only processes comments from AUTHORIZED_USER. Public repos allow
# anyone to comment — filtering prevents prompt injection via PR comments.
#
# Usage: select_prs.sh REPO AUTHORIZED_USER
# Output: JSON {"tier": N, "prs": [...]} on stdout
set -euo pipefail

REPO="${1:?Usage: select_prs.sh REPO AUTHORIZED_USER}"
AUTHORIZED_USER="${2:?Usage: select_prs.sh REPO AUTHORIZED_USER}"

# Fetch open PRs with comments, reviews, and commit data
PR_DATA=$(gh pr list \
    --repo "$REPO" \
    --state open \
    --json number,title,headRefName,body,labels,comments,reviews,commits \
    --limit 50 2>/dev/null || echo "[]")

# Classify PRs into tiers
echo "$PR_DATA" | AUTHORIZED_USER="$AUTHORIZED_USER" python3 -c "
import sys, json, os, random

data = json.loads(sys.stdin.read())
authorized_user = os.environ['AUTHORIZED_USER']

tier1 = []
tier2 = []

for pr in data:
    labels = {l['name'] for l in pr.get('labels', [])}
    if 'in-progress' in labels:
        continue

    commits = pr.get('commits', [])
    if not commits:
        continue

    latest_commit_time = max(c.get('committedDate', '') for c in commits)

    # Security: only process comments/reviews from authorized user
    comments = pr.get('comments', [])
    auth_comments = [
        c for c in comments
        if c.get('author', {}).get('login') == authorized_user
    ]

    reviews = pr.get('reviews', [])
    auth_reviews = [
        r for r in reviews
        if r.get('author', {}).get('login') == authorized_user
    ]

    # Tier 1: authorized user left feedback after latest commit
    latest_feedback = ''
    if auth_comments:
        latest_feedback = max(c.get('createdAt', '') for c in auth_comments)
    if auth_reviews:
        ts = max(r.get('submittedAt', '') for r in auth_reviews)
        latest_feedback = max(latest_feedback, ts)

    if latest_feedback and latest_commit_time and latest_feedback > latest_commit_time:
        pr['_auth_comments'] = auth_comments
        pr['_auth_reviews'] = auth_reviews
        tier1.append(pr)
        continue

    # Tier 2: no feedback from anyone
    if not comments and not reviews:
        tier2.append(pr)
        continue

if tier1:
    random.shuffle(tier1)
    print(json.dumps({'tier': 1, 'prs': tier1}))
elif tier2:
    random.shuffle(tier2)
    print(json.dumps({'tier': 2, 'prs': tier2}))
else:
    print(json.dumps({'tier': 3, 'prs': []}))
"
