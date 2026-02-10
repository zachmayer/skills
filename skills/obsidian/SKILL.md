---
name: obsidian
description: >
  Read, write, and search notes in an Obsidian vault stored as plain markdown files.
  Use when the user wants to create a note, find a note, list notes, or link notes together.
  Do NOT use for code-specific documentation (use CLAUDE.md or AGENTS.md instead).
allowed-tools: Bash(git *), Read, Write, Glob, Grep
---

Manage notes in the Obsidian vault at `~/claude/obsidian/`. Follows the **MOC (Map of Content)** pattern: atomic notes linked through hub pages.

## Vault Structure

```
~/claude/obsidian/
├── memory/              # Hierarchical memory (managed by hierarchical_memory skill)
│   ├── memory.md        # Overall working memory
│   ├── 2026-02.md       # Monthly summaries
│   └── 2026-02-08.md    # Daily notes (append-only)
├── heartbeat/           # Autonomous task queue
│   └── tasks.md
└── Zach/                # Personal knowledge (curated, durable)
    ├── Interests/       # Hobbies, games, media
    ├── Personal/        # Family, life
    ├── Technical/       # Tech notes, equipment, troubleshooting
    └── Work/            # Career, projects, business
```

## Note Patterns

### Atomic notes + MOC (preferred)

Each topic gets a **Map of Content** (MOC) hub note that links to smaller atomic notes. This is the default pattern for any topic with 2+ sub-topics.

```markdown
# Factorio                          ← MOC hub
#gaming #factorio

## Topics
- [[Factorio Base Designs]] — layout philosophies
- [[Factorio Server Setup]] — headless server, RCON
- [[Factorio Gleba Farm]] — optimized blueprint
```

Each atomic note links back to its hub and to related siblings:

```markdown
# Factorio Gleba Farm               ← atomic note
#factorio #space-age #blueprint

Source: https://factoriobin.com/post/mrx1ek/2
Grabbed: 2026-02-09

...content...

## Related
- [[Factorio]]
- [[Factorio Space Exploration]]
```

### When to create a MOC vs a standalone note

- **New topic, first note** — create a standalone note. It becomes the MOC later if the topic grows.
- **Second note on same topic** — split the original into a MOC hub + atomic notes.
- **Web grabs** — always create atomic notes. Link to an existing MOC or create one if a related topic exists.

## Conventions

- Use descriptive filenames as note titles (spaces are fine: `Factorio Base Designs.md`)
- Add `#topic` tags for graph discoverability
- Add `[[wiki-links]]` to reference related notes (filename without `.md`)
- Memory files in `memory/` are managed by `hierarchical_memory` — don't edit directly
- After changes: `git -C ~/claude/obsidian add -A && git -C ~/claude/obsidian commit -m "note: description" && git -C ~/claude/obsidian push`
- If no remote is configured, use the `private_repo` skill to set one up
