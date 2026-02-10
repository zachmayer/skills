---
name: obsidian
description: >
  Read, write, and search notes in an Obsidian vault stored as plain markdown files.
  Use when the user wants to create a note, find a note, list notes, or link notes together.
  Do NOT use for code-specific documentation (use CLAUDE.md or AGENTS.md instead).
allowed-tools: Bash(git *), Read, Write, Glob, Grep
---

Manage notes in the Obsidian vault. The vault root is set by `CLAUDE_OBSIDIAN_DIR` (default: `~/claude/obsidian`). Follows a **nested MOC (Map of Content)** pattern: atomic notes linked through hub pages in a hub-and-spoke hierarchy.

## Vault Structure

```
$CLAUDE_OBSIDIAN_DIR/            # default: ~/claude/obsidian
├── memory/                      # Hierarchical memory (managed by hierarchical_memory skill)
│   ├── overall_memory.md        # Overall working memory
│   ├── 2026-02.md               # Monthly summaries
│   └── 2026-02-08.md            # Daily notes (append-only)
├── heartbeat/                   # Autonomous task queue
│   └── tasks.md
└── knowledge_graph/             # Durable topic notes, personal knowledge
```

## Note Patterns

### Nested MOC (hub-and-spoke)

The knowledge graph uses **nested MOCs** — hubs that link to sub-hubs, which link to atomic notes. This is standard Obsidian hub-and-spoke at multiple levels.

```
Factorio (top MOC)
├── Factorio Gleba (sub-MOC)
│   ├── Factorio Gleba Farm (atomic)
│   ├── Factorio Gleba Starter Factory (atomic)
│   └── Factorio Artificial Jellynut Soil (atomic)
├── Factorio Quality (sub-MOC)
│   ├── Factorio Comprehensive Quality Guide (atomic)
│   └── ...
├── Factorio Base Designs (atomic — not enough notes for a sub-hub yet)
└── ...
```

**Rules:**
- **Atomic notes link up to their nearest hub**, not the top-level MOC
- **Sub-MOCs link both up and down** — `Related: [[Factorio]]` + a Topics list of children
- **Promote to sub-MOC when a topic accumulates 3+ atomic notes** — before that, link directly from the parent

### MOC hub example

```markdown
# Factorio                          ← top-level MOC
#gaming #factorio

## Topics
- [[Factorio Gleba]] — biological planet: farms, factories, soil
- [[Factorio Base Designs]] — layout philosophies
```

### Atomic note example

```markdown
# Factorio Gleba Farm               ← links to nearest hub, not top MOC
#factorio #space-age #gleba

Source: https://factoriobin.com/post/mrx1ek/2
Grabbed: 2026-02-09

...content...

## Related
- [[Factorio Gleba]]
- [[Factorio Space Exploration]]
```

### When to create or promote a MOC

- **New topic, first note** — create a standalone atomic note. Link to parent MOC.
- **3+ notes on a sub-topic** — promote: create a sub-MOC hub, move atomic links under it, update parent MOC to point to the sub-hub.
- **Web grabs** — always create atomic notes. Link to the nearest existing hub or create one.

## Finding Notes

Use Grep and Glob on the vault directory to find notes:

```bash
# Find notes by filename
Glob("$CLAUDE_OBSIDIAN_DIR/**/*.md")

# Search note contents
Grep(pattern="search term", path="$CLAUDE_OBSIDIAN_DIR/")
```

## Conventions

- Use descriptive filenames as note titles (spaces are fine: `Factorio Base Designs.md`)
- Add `#topic` tags for graph discoverability
- Add `[[wiki-links]]` to reference related notes (filename without `.md`)
- Memory files in `memory/` are managed by `hierarchical_memory` — don't edit directly
- After changes: `git -C $CLAUDE_OBSIDIAN_DIR add -A && git -C $CLAUDE_OBSIDIAN_DIR commit -m "note: description" && git -C $CLAUDE_OBSIDIAN_DIR push`
- If no remote is configured, use the `private_repo` skill to set one up
