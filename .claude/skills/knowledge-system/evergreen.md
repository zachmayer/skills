Periodic maintenance for the Obsidian vault and git repos.

## Knowledge Graph Health

Check `$CLAUDE_OBSIDIAN_DIR/knowledge_graph/` for:

- **Orphan notes**: Notes not linked from any hub or other note. Use Grep to find all `[[wikilinks]]` across the vault, then Glob to list all note files. Notes whose title appears in no other file's wikilinks are orphans. Link them to an appropriate hub or create one.
- **Broken wikilinks**: `[[targets]]` that don't resolve to any `.md` file in the vault. Rename the link or create the missing note.
- **Missing metadata**: Notes without `Source:` or `Date:` lines. Every knowledge graph note needs both (see [obsidian.md](obsidian.md)). Add them.

## Memory Health

Check `$CLAUDE_OBSIDIAN_DIR/memory/` for:

- **Aggregation staleness**: Run `uv run --directory KNOWLEDGE_SYSTEM_DIR python scripts/memory.py status` (where `KNOWLEDGE_SYSTEM_DIR` is the directory containing the `knowledge-system` skill). Aggregate any stale months.
- **Fact drift**: Scan `overall_memory.md` for facts whose velocity suggests they may be stale (see [hierarchical-memory.md](hierarchical-memory.md) Fact Freshness section). Flag for user confirmation.

## Repo Health

- **Stale branches**: `git branch --merged main` shows branches already merged. Delete them with `git branch -d <name>`.
- **Dangling worktrees**: `git worktree list` then `git worktree prune`.
- The heartbeat runner already cleans its own branches — this is for organic accumulation in the main repo.

## When to Run

- Heartbeat: when no urgent issues are available, spend remaining time on maintenance
- Manual: when the user asks to tidy up or the vault feels cluttered
- Don't force it — maintenance is lower priority than issue work
