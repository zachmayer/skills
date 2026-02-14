---
name: evergreen
description: >
  Generalized housekeeping that runs periodically (heartbeat or manual). Three scopes:
  repo-scoped (prune branches, worktrees), knowledge-scoped (orphans, broken links, missing metadata),
  and memory-scoped (duplicate entries). Use when the agent environment has accumulated clutter
  from parallel agents, stale branches, or organic growth. Do NOT use for one-time cleanup of a
  specific file or note.
---

Maintenance skill for keeping repos, knowledge graph, and memory clean. Run periodically via heartbeat or manually when things feel cluttered.

## Usage

```bash
# Repo maintenance (dry run — report only)
uv run python skills/evergreen/scripts/evergreen.py repo /path/to/repo

# Repo maintenance (actually prune merged branches and dangling worktrees)
uv run python skills/evergreen/scripts/evergreen.py repo /path/to/repo --prune

# Knowledge graph maintenance (orphans, broken links, duplicates, missing metadata)
uv run python skills/evergreen/scripts/evergreen.py knowledge

# Memory maintenance (duplicate entries across daily notes)
uv run python skills/evergreen/scripts/evergreen.py memory

# Run all scopes
uv run python skills/evergreen/scripts/evergreen.py all /path/to/repo
uv run python skills/evergreen/scripts/evergreen.py all --prune /path/to/repo
```

## Scopes

### Repo-scoped
- **Merged branches**: local branches already merged into main/master
- **Dangling worktrees**: worktree directories that no longer exist on disk
- Use `--prune` to actually delete (default is dry-run report)

### Knowledge-scoped
- **Orphan notes**: knowledge graph notes not linked from any other note
- **Broken wikilinks**: `[[targets]]` that don't resolve to any file
- **Duplicate names**: same filename in different subdirectories
- **Missing metadata**: notes without `Source:` or `Date:` lines

### Memory-scoped
- **Duplicate entries**: identical log entries appearing across multiple daily notes
- Normalizes entries (strips timestamps and context tags) before comparing

## Heartbeat Integration

When running as heartbeat, include evergreen as a periodic task:

1. Run `evergreen.py all /path/to/repo` to get a report
2. Review findings — orphans and broken links often indicate notes that should be linked or renamed
3. Use `--prune` for repo cleanup only after confirming the branches are truly stale
4. For knowledge/memory issues, fix manually or create targeted issues

## Environment

- `CLAUDE_OBSIDIAN_DIR`: vault root (default: `~/claude/obsidian`)
