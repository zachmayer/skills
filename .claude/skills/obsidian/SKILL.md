---
name: obsidian
description: >
  Read, write, and search notes in an Obsidian vault stored as plain markdown files.
  Use when the user wants to create a note, find a note, list notes, or link notes together.
  Do NOT use for code-specific documentation (use CLAUDE.md or AGENTS.md instead).
allowed-tools: Bash(git *), Bash(obsidian *), Read, Write, Glob, Grep
---

Manage notes in the Obsidian vault. The vault root is set by `CLAUDE_OBSIDIAN_DIR` (default: `~/claude/obsidian`). Follows a **nested MOC (Map of Content)** pattern: atomic notes linked through hub pages in a hub-and-spoke hierarchy.

## MANDATORY: Source and Date Metadata

**Every note that has a source MUST include these metadata lines** immediately after the title and tags. This is non-negotiable:

```markdown
Source: <URL or reference — where did this information come from?>
Date: <YYYY-MM-DD — when was this note created?>
```

- Web grabs: `Source:` is the original URL, `Date:` is when it was fetched
- Session notes: `Source:` is "Claude Code session", `Date:` is today
- Manual notes: `Source:` is whatever the user provides, `Date:` is today
- If there is genuinely no source (pure original thought), use `Source: original` with `Date:` still required

**A note without a Date is always broken.** A note without a Source is broken unless there is genuinely no source.

## Staleness Detection

When reading notes, consider whether the content may have drifted since the `Date:` field. Use judgment based on **information velocity** — how fast that kind of information typically changes:

- **Notes with a URL `Source:`** — if the topic moves fast (library docs, API references, news), offer to re-fetch via `web_grab`. A 3-month-old note about a Python library is probably stale; a note about a historical event is not.
- **Notes with personal facts** — if a note records something that could have changed (current project, team structure, tool preferences), ask the user to confirm rather than assuming. See the `hierarchical_memory` skill's Fact Freshness section for velocity guidance.

Don't over-flag — most notes age fine. Focus on notes you're actively relying on for decisions.

## Vault Structure

```
$CLAUDE_OBSIDIAN_DIR/            # default: ~/claude/obsidian
├── memory/                      # Hierarchical memory (managed by hierarchical_memory skill)
│   ├── overall_memory.md        # Overall working memory
│   ├── 2026-02.md               # Monthly summaries
│   └── 2026-02-08.md            # Daily notes (append-only)
└── knowledge_graph/             # Durable topic notes, personal knowledge
```

## Obsidian CLI

The Obsidian CLI (v1.12.4+) communicates with the running Obsidian app. It provides link-aware search, task management, properties, and template-based creation that direct file ops cannot replicate.

### Prerequisites

1. Obsidian v1.12+ with Catalyst license
2. Enable: **Settings → General → Command line interface**
3. Restart terminal (macOS adds `/Applications/Obsidian.app/Contents/MacOS` to PATH via `~/.zprofile`)
4. Obsidian must be **running** for commands to work

### When to Use CLI vs Direct File Ops

| Use CLI | Use direct file ops (Read/Write/Glob/Grep) |
|---------|---------------------------------------------|
| Search (returns ranked results) | Simple file reads/writes |
| Task queries across vault | Bulk text operations |
| Property get/set (typed metadata) | Grep for exact strings |
| Template-based note creation | Creating notes without templates |
| Link graph queries (backlinks, orphans) | Known file paths |
| Daily note append (respects daily note plugin config) | Memory files (managed by hierarchical_memory) |

### Key Commands

**Search:**
```shell
obsidian search query="..." limit=10 format=json
obsidian search:context query="..."              # includes surrounding context
```

**Files:**
```shell
obsidian read file=NoteName                      # read by wikilink name
obsidian create name=Title path=folder/ content="..." template=TemplateName
obsidian append file=NoteName content="new text"
obsidian move file=NoteName to=new/folder/
obsidian files folder=knowledge_graph sort=modified limit=20
```

**Daily notes:**
```shell
obsidian daily                                   # open today's daily note
obsidian daily:read                              # print today's note
obsidian daily:append content="- new item"
```

**Tasks:**
```shell
obsidian tasks todo                              # incomplete tasks in active file
obsidian tasks daily                             # tasks from daily note
obsidian task file=NoteName line=8 toggle        # toggle a specific task
```

**Properties:**
```shell
obsidian properties file=NoteName
obsidian property:set name=status value=done type=text file=NoteName
obsidian property:read name=tags file=NoteName
```

**Links:**
```shell
obsidian backlinks file=NoteName                 # incoming links
obsidian links file=NoteName                     # outgoing links
obsidian orphans                                 # files with no incoming links
obsidian unresolved                              # broken wikilinks
```

**Tags:**
```shell
obsidian tags sort=count                         # all tags by frequency
obsidian tag name=factorio verbose               # files with a specific tag
```

**Vault targeting** (when multiple vaults exist):
```shell
obsidian vault="My Vault" search query="test"
```

All commands support `--copy` to copy output to clipboard.

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
Date: 2026-02-09

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

Multiple search strategies, from fastest to deepest:

1. **Tags and links** — follow `#tags` and `[[wiki-links]]` to navigate the hub-and-spoke graph. Start from a MOC hub and walk the links. Best when you know the topic area.
2. **Glob** — find notes by filename pattern. Fast for known titles.
3. **Grep** — exact text search. Best for specific terms, error messages, or names.
4. **Obsidian CLI search** — `obsidian search query="..." format=json` returns ranked results using Obsidian's index. Best for natural language queries when Obsidian is running.
5. **Semantic search** — if `jina-grep` is installed (`make install-jina-grep`), use it for natural language queries. Works standalone or as a reranker on grep output:

```bash
# By filename
Glob("$CLAUDE_OBSIDIAN_DIR/**/*.md")

# Exact text search
Grep(pattern="search term", path="$CLAUDE_OBSIDIAN_DIR/")

# Semantic search (natural language)
jina-grep -r --top-k 5 "your question in plain English" $CLAUDE_OBSIDIAN_DIR/

# Semantic reranking of grep results
grep -rn "token" $CLAUDE_OBSIDIAN_DIR/ | jina-grep "OAuth refresh race condition"
```

## Conventions

- Use descriptive filenames as note titles (spaces are fine: `Factorio Base Designs.md`)
- Add `#topic` tags for graph discoverability
- Add `[[wiki-links]]` to reference related notes (filename without `.md`)
- Memory files in `memory/` are managed by `hierarchical_memory` — don't edit directly
- After changes, run these commands sequentially:
  ```bash
  git -C $CLAUDE_OBSIDIAN_DIR add -A
  git -C $CLAUDE_OBSIDIAN_DIR commit -m "note: description"
  git -C $CLAUDE_OBSIDIAN_DIR push
  ```
- If no remote is configured, use the `private_repo` skill to set one up
