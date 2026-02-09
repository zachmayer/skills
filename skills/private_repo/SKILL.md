---
name: private_repo
description: >
  Create or connect a private GitHub repository for backing up sensitive local
  data (memory, notes, config). Use when another skill needs git-backed storage
  with a private remote, when the user mentions wanting to back up or sync
  local data, or when you detect a ~/claude directory without a remote.
  Do NOT use for public repos or code projects.
allowed-tools: Bash(gh *), Bash(git *)
---

Help the user set up a private GitHub repository for local data that should be backed up but kept private.

## Flow

### 1. Check current state

```bash
git -C TARGET_DIR remote get-url origin 2>/dev/null
```

If a remote already exists, confirm with the user and skip to step 4.

### 2. Ask the user

Present these options:
- **Create a new private repo** (recommended if they don't have one)
- **Connect an existing private repo** (if they already have one)
- **Skip** (no remote, local git only)

### 3a. Create a new repo with gh CLI

```bash
gh repo create REPO_NAME --private --description "Private backup for DESCRIPTION"
```

Then set up the remote (use `git -C` to match the `Bash(git *)` permission):

```bash
git -C TARGET_DIR init && git -C TARGET_DIR add -A && git -C TARGET_DIR commit -m "initial commit"
git -C TARGET_DIR remote add origin git@github.com:USERNAME/REPO_NAME.git
git -C TARGET_DIR push -u origin main
```

Use `gh api user --jq '.login'` to get the username.

### 3b. Connect an existing repo

```bash
git -C TARGET_DIR init && git -C TARGET_DIR remote add origin REPO_URL
git -C TARGET_DIR pull origin main --allow-unrelated-histories
git -C TARGET_DIR add -A && git -C TARGET_DIR commit -m "merge local state" && git -C TARGET_DIR push
```

### 4. Confirm sync works

```bash
git -C TARGET_DIR push
```

## Common Uses

This skill is called by other skills that need private remote storage:

- **hierarchical_memory**: backs up `~/claude/memory/` - suggest repo name `claude-memory-private`
- **obsidian**: backs up `~/claude/obsidian/` - repo name `obsidian-vault-private`

## Important

- Always create repos as **private** -- this data may contain personal notes, API keys, or sensitive context
- Use SSH URLs (`git@github.com:...`) over HTTPS when possible
- If `gh` is not installed or not authenticated, walk the user through manual GitHub repo creation
