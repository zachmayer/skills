---
name: trufflehog
description: >
  Scan for leaked secrets using TruffleHog. Use WHEN the user asks to scan for
  secrets, check for leaked API keys, audit credentials, find hardcoded passwords,
  or review code for secret leaks. Do NOT use for vulnerability scanning (CVE),
  dependency audits, or general security audits beyond secret detection.
allowed-tools: Bash(trufflehog *)
---

# TruffleHog

## Gotchas

- **Git repos need `file://` prefix**: `trufflehog git file://.` not `trufflehog git .`
- **Use `git` subcommand for git repos**, not `filesystem` -- git's internal compression requires TruffleHog's git-aware scanner to search history properly
- **Always pass `--json`** for structured output you can parse
- **`--only-verified` requires network** -- it tests credentials against provider APIs
- **`--fail` exits 183** (not 1) when secrets are found
- **`--concurrency=1`** prevents rate limiting during verification on large repos
- **Inline suppression**: `# trufflehog:ignore` comment on a line to skip known non-secrets

## Commands

Scan current repo's full git history:

```bash
trufflehog git file://. --only-verified --json
```

Scan only recent commits (PR review / CI):

```bash
trufflehog git file://. --since-commit main --only-verified --fail --json
```

Scan non-git directory:

```bash
trufflehog filesystem /path/to/dir --force-skip-binaries --force-skip-archives --json
```

Scan a GitHub org (includes wikis):

```bash
trufflehog github --org=ORG_NAME --issue-comments --pr-comments --only-verified --json
```

## Interpreting Results

Each JSON finding has `Verified` (bool), `DetectorName` (secret type), `Raw` (the secret), and `SourceMetadata` (file, commit, line).

- **Verified=true**: Live credential. Rotate immediately, then scrub from git history with git filter-repo or BFG.
- **Verified=false**: May be expired, test key, or false positive. Review manually.
- High-entropy strings without a known detector are usually false positives.

Save results for analysis: pipe output to `~/claude/scratch/trufflehog-results.json`.
