---
name: trufflehog
description: >
  Scan for leaked secrets and credentials using TruffleHog. Use WHEN the user
  asks to scan a repo for secrets, check for leaked API keys, audit credentials,
  find hardcoded passwords, run a security scan, or set up pre-commit secret
  detection. Also use when reviewing code for security and secrets are a concern.
  Do NOT use for general security audits beyond secret detection, vulnerability
  scanning (use a CVE scanner), or dependency audits (use uv audit or similar).
allowed-tools: Bash(trufflehog *)
---

# TruffleHog Secret Scanning

TruffleHog finds and verifies leaked credentials in git repos, filesystems, and more. It classifies 800+ secret types and can verify whether detected secrets are still active.

## Installation

Check if installed:

```bash
trufflehog --version
```

If not installed:

```bash
brew install trufflehog
```

## Core Commands

### Scan a Git Repository (Most Common)

Scan the full git history of the current repo for secrets:

```bash
trufflehog git file://. --json
```

Always use the git subcommand (not filesystem) for git repos. Git internal compression requires a separate workflow. The path must be prefixed with file://.

Scan only verified (confirmed-active) secrets to reduce false positives:

```bash
trufflehog git file://. --only-verified --json
```

Scan a remote repo directly:

```bash
trufflehog git https://github.com/OWNER/REPO --only-verified --json
```

### Scan Since a Specific Commit (CI / PR Review)

Scan only new commits, useful for reviewing a PR branch:

```bash
trufflehog git file://. --since-commit HEAD~5 --json
```

Scan changes since divergence from main:

```bash
trufflehog git file://. --since-commit main --json
```

Use --fail to exit with code 183 if secrets are found (useful for CI gates):

```bash
trufflehog git file://. --since-commit main --only-verified --fail --json
```

### Scan Files on Disk (Non-Git)

For directories that are not git repos, or for corrupted repos:

```bash
trufflehog filesystem /path/to/directory --json
```

Scan multiple paths:

```bash
trufflehog filesystem /path/to/dir1 /path/to/dir2 --json
```

Skip binaries and archives to reduce noise:

```bash
trufflehog filesystem /path/to/directory --force-skip-binaries --force-skip-archives --json
```

### Scan a GitHub Organization

Scan all repos in a GitHub org, including wikis and comments:

```bash
trufflehog github --org=ORG_NAME --only-verified --json
```

Include issue and PR comments (often overlooked secret sources):

```bash
trufflehog github --org=ORG_NAME --issue-comments --pr-comments --only-verified --json
```

### Scan from stdin

Pipe content directly:

```bash
cat suspect-file.txt | trufflehog stdin --json
```

## Reading Results

### JSON Output Fields

Each finding in --json output includes:

- **DetectorName**: The type of secret (e.g., AWS, GitHub, Slack, PrivateKey)
- **Verified**: true if TruffleHog confirmed the credential is live
- **Raw**: The raw secret value
- **SourceMetadata**: Where it was found (file path, commit, line number)
- **ExtraData**: Additional context (e.g., AWS account ID, key permissions)

### Verification Statuses

- **verified**: Credential confirmed active by testing against the provider API
- **unverified**: Detected but not confirmed valid (may be expired, rotated, or a false positive)
- **unknown**: Verification attempted but failed (network error, rate limit, etc.)

### Prioritizing Findings

1. **Verified secrets are urgent** -- they are live credentials that need immediate rotation
2. **Unverified secrets** -- review manually; may be test keys, expired, or false positives
3. **High-entropy strings** without a known detector -- usually false positives, low priority

## Common Workflows

### Pre-commit Secret Scanning

Run before committing to catch secrets early:

```bash
trufflehog git file://. --since-commit HEAD --only-verified --fail
```

### Audit a Repo Before Open-Sourcing

Full history scan with verification:

```bash
trufflehog git file://. --only-verified --json | tee ~/claude/scratch/trufflehog-results.json
```

Review the results, then for any verified secrets:
1. Rotate the credential immediately at the provider
2. Use git filter-repo or BFG Repo-Cleaner to remove from history
3. Re-scan to confirm removal

### Quick Security Check on Current Codebase

Scan just the working directory files (no git history):

```bash
trufflehog filesystem . --force-skip-binaries --json
```

### Scan with Reduced Noise

Use --only-verified and --concurrency=1 to avoid rate limiting during verification:

```bash
trufflehog git file://. --only-verified --concurrency=1 --json
```

## Suppressing Known False Positives

Add a comment on the line containing the known non-secret:

```
EXAMPLE_KEY=not-a-real-key  # trufflehog:ignore
```

## Tips

- Always use --json for machine-readable output that is easier to analyze
- Use the git subcommand for git repos, filesystem for plain directories
- --only-verified dramatically reduces false positives but requires network access
- Save results to ~/claude/scratch/ for further analysis
- --fail (exit code 183) is useful for CI gates and pre-commit hooks
- --concurrency=1 prevents rate limiting when verifying many secrets
- For large repos, --force-skip-binaries --force-skip-archives speeds up scans
