---
name: obsidian
description: >
  Read, write, and search notes in an Obsidian vault stored as plain markdown files.
  Use when the user wants to create a note, find a note, list notes, or link notes together.
  Do NOT use for code-specific documentation (use CLAUDE.md or AGENTS.md instead).
allowed-tools: Bash(git *), Read, Write, Glob, Grep
---

Manage notes in the Obsidian vault at `~/claude/obsidian/`.

Notes are plain markdown files. Use `[[Note Title]]` wiki-links to connect related notes (matching filename without `.md`).

## Vault Structure

```
~/claude/obsidian/
├── memory/              # Hierarchical memory (managed by hierarchical_memory skill)
│   ├── memory.md        # Overall working memory
│   ├── 2026-02.md       # Monthly summaries
│   └── 2026-02-08.md    # Daily notes (append-only)
├── heartbeat/           # Autonomous task queue
│   └── tasks.md
├── todo/                # TODO lists
│   ├── human.md         # Tasks requiring human action
│   └── claude.md        # Tasks Claude can do autonomously
├── personal/            # Personal knowledge (curated, durable)
│   ├── work/
│   ├── technical/
│   └── interests/
└── ...                  # Other topic notes
```

## Conventions

- Use descriptive filenames as note titles
- Add `[[wiki-links]]` to reference related notes
- Memory files in `memory/` are managed by the `hierarchical_memory` skill — don't edit directly
- Curated knowledge goes in topic directories; daily work goes in `memory/`
- After changes, commit with `git -C ~/claude/obsidian add -A && git -C ~/claude/obsidian commit -m "note: description" && git -C ~/claude/obsidian push`
- If no remote is configured, use the `private_repo` skill to set one up
