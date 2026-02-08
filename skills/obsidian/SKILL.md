---
name: obsidian
description: >
  Read, write, and search notes in an Obsidian vault stored as plain markdown files.
  Use when the user wants to create a note, find a note, list notes, or link notes together.
  Do NOT use for code-specific documentation (use CLAUDE.md or AGENTS.md instead).
allowed-tools: Bash(git *), Read, Write, Glob, Grep
---

Manage notes in the Obsidian vault at `~/.claude/obsidian/`.

All notes are plain markdown files (`.md`). Obsidian uses `[[wiki-links]]` to link between notes. When referencing another note, use `[[Note Title]]` syntax (matching the filename without the `.md` extension).

## Operations

### Create a note

Write a markdown file to the vault:

```
Write ~/.claude/obsidian/Note Title.md
```

- Use a descriptive filename as the note title
- Add `[[wiki-links]]` to reference related notes
- Organize with subdirectories when appropriate (e.g. `~/.claude/obsidian/projects/`, `~/.claude/obsidian/daily/`)

### Search notes

Search note contents by keyword or pattern:

```
Grep pattern ~/.claude/obsidian/
```

### List notes

List all notes or notes in a subdirectory:

```
Glob ~/.claude/obsidian/**/*.md
```

### Read a note

```
Read ~/.claude/obsidian/Note Title.md
```

### Link notes

When creating or editing notes, add `[[wiki-links]]` to connect related notes. For example:

```markdown
## Meeting Notes

Discussed the [[Project Alpha]] roadmap with [[Alice]].
Follow-up tasks are tracked in [[2026-02-08 TODO]].
```

## Git Integration

After creating or modifying notes, commit and push:

```bash
cd ~/.claude/obsidian && git add -A && git commit -m "note: brief description" && git push 2>/dev/null; true
```

### First-time setup

```bash
mkdir -p ~/.claude/obsidian && cd ~/.claude/obsidian && git init
```

### Remote sync

If no remote is configured, use the `private_repo` skill to create or connect a private GitHub repo for `~/.claude/obsidian/`.

## When the User Asks

- "Save this..." or "Note this..." or "Write this down..." -> Create a note, then git commit
- "Find notes about..." or "Search for..." -> Use Grep to search note contents
- "What notes do I have?" or "List notes..." -> Use Glob to list files
- "Link these notes..." -> Edit notes to add `[[wiki-links]]` between them
