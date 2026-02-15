# Heartbeat Machine Account Setup

The heartbeat agent pushes branches and creates PRs. By default it uses the repo owner's credentials, which means the owner can't use GitHub's "Require review from someone other than the last pusher" branch protection rule — the agent IS the owner.

A dedicated machine account fixes this: the bot pushes and opens PRs, the human reviews and merges.

## 1. Create the GitHub account

1. Create a new GitHub account (e.g. `skills-heartbeat-bot`).
   - Use a dedicated email address.
   - Choose a username that clearly identifies it as a bot.
2. Add the account as a **collaborator** on your repo with **Write** access.
   - Settings → Collaborators → Add people.
   - Write access lets it push branches and create PRs but not change settings.

## 2. Create a fine-grained Personal Access Token

On the machine account (not your main account):

1. Go to Settings → Developer settings → Personal access tokens → Fine-grained tokens.
2. Create a new token with:
   - **Repository access**: Only select repositories → pick your repo.
   - **Permissions**:
     - Contents: Read and write (push branches)
     - Pull requests: Read and write (create PRs)
     - Issues: Read (list issues for work queue)
   - **Expiration**: 1 year (set a reminder to rotate).
3. Copy the token.

## 3. Configure heartbeat.env

Add the token and git identity to `~/.claude/heartbeat.env`:

```bash
# Claude Code auth (existing)
export CLAUDE_CODE_OAUTH_TOKEN="your-oauth-token"

# Machine account GitHub token
export GH_TOKEN="github_pat_..."

# Machine account git identity
export GIT_AUTHOR_NAME="skills-heartbeat[bot]"
export GIT_AUTHOR_EMAIL="123456+skills-heartbeat-bot@users.noreply.github.com"
export GIT_COMMITTER_NAME="skills-heartbeat[bot]"
export GIT_COMMITTER_EMAIL="123456+skills-heartbeat-bot@users.noreply.github.com"
```

Find the noreply email: machine account → Settings → Emails → "Keep my email addresses private" shows the `ID+username@users.noreply.github.com` address.

Ensure permissions are locked down:

```bash
chmod 600 ~/.claude/heartbeat.env
```

## 4. Enable branch protection

Now that PRs come from a different account, enable review requirements:

1. Settings → Branches → Branch protection rules → Add rule.
2. Branch name pattern: `main`.
3. Enable:
   - **Require a pull request before merging**
   - **Require approvals** (1)
   - **Require review from Code Owners** (optional, requires CODEOWNERS file)
   - **Do not allow bypassing the above settings** (optional, prevents even admins from merging without review)

## How it works

No changes to `heartbeat.sh` are needed. The script already sources `~/.claude/heartbeat.env`, which sets environment variables. The `gh` CLI automatically uses `GH_TOKEN` when set, and git uses `GIT_AUTHOR_*`/`GIT_COMMITTER_*` for commit identity. The machine account's token scopes limit what the agent can do — no admin access, no settings changes, no force pushes.

## Verification

After setup, run a test heartbeat and verify:

```bash
make test-heartbeat
```

Then check:
- PR author shows the machine account username, not the repo owner.
- Commits show the machine account's name and email.
- The repo owner can review and merge the PR (not blocked by "can't self-review").
