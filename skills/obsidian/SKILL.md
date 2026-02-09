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

## Conventions

- Use descriptive filenames as note titles
- Add `[[wiki-links]]` to reference related notes
- Organize with subdirectories (e.g. `projects/`, `daily/`)
- After creating or modifying notes, commit and push to `~/claude/obsidian/`
- If no remote is configured, use the `private_repo` skill to set one up
