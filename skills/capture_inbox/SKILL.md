---
name: capture_inbox
description: >
  Smart routing for any input. Routes by scope + audience to the right
  destination: memory daily log (ephemeral), GitHub Issues with agent-task
  label (agent work), obsidian knowledge_graph (durable knowledge),
  CLAUDE.md (repo-specific agent guidance), or README.md (repo dev memory).
  Use when the user says "capture this", "save this", "inbox", "route this",
  or provides raw input that needs to be filed somewhere.
  Do NOT use when the user specifies an exact destination (use that skill directly).
---

Smart inbox that routes any input to the right destination. One entry point, five exits.

## When the user invokes this skill

They provide raw input — a thought, a finding, a task, a preference, a decision. Your job: classify it, route it, confirm.

## Routing Decision

Classify the input on three axes, then route:

### Axis 1: Durability

| Signal | Classification |
|--------|---------------|
| Fleeting thought, status update, "today I..." | **Ephemeral** |
| Architectural decision, research finding, reference material | **Durable** |
| Actionable work item, bug report, feature idea | **Task** |
| Instruction for how the agent should behave | **Guidance** |

### Axis 2: Scope

| Signal | Classification |
|--------|---------------|
| About a specific repo's code, build, or conventions | **Repo-specific** |
| About the user's tools, preferences, personal knowledge | **Personal** |
| About a project that spans multiple repos | **Cross-project** |

### Axis 3: Audience

| Signal | Classification |
|--------|---------------|
| For the agent to act on autonomously | **Agent** |
| For future humans reading the repo | **Human** |
| For the user's own future reference | **Self** |

### Route Table

| Durability | Scope | Audience | Destination |
|-----------|-------|----------|-------------|
| Ephemeral | Any | Any | **Memory daily log** |
| Durable | Personal | Self | **Obsidian knowledge_graph** |
| Durable | Cross-project | Self | **Obsidian knowledge_graph** |
| Durable | Repo-specific | Human | **README.md** (dev memory section) |
| Task | Any | Agent | **GitHub Issue** (agent-task label) |
| Task | Any | Human | **GitHub Issue** (no agent-task label) |
| Guidance | Repo-specific | Agent | **CLAUDE.md** |
| Guidance | Personal | Agent | **Obsidian knowledge_graph** (agent preferences note) |

When the classification is ambiguous, ask the user. When multiple destinations apply, route to each.

## Routing Actions

### Memory daily log (ephemeral)

Use `hierarchical_memory` to append a timestamped note:

```bash
uv run --directory MEMORY_SKILL_DIR python scripts/memory.py note "CAPTURED_TEXT"
```

Where `MEMORY_SKILL_DIR` is the `hierarchical_memory` skill directory.

### Obsidian knowledge_graph (durable knowledge)

Create or update an atomic note in the obsidian vault following the `obsidian` skill conventions:

1. Search for existing notes on the topic: `Grep(pattern="keyword", path="$CLAUDE_OBSIDIAN_DIR/knowledge_graph/")`
2. If a related note exists, update it. Otherwise create a new atomic note.
3. Include mandatory metadata:
   ```markdown
   # Note Title
   #topic-tag

   Source: <where this came from — URL, conversation, user input>
   Date: YYYY-MM-DD

   <content>

   ## Related
   - [[Nearest Hub Note]]
   ```
4. Link to the nearest existing MOC hub.
5. Commit and push:
   ```bash
   git -C $CLAUDE_OBSIDIAN_DIR add -A && git -C $CLAUDE_OBSIDIAN_DIR commit -m "capture: <summary>" && git -C $CLAUDE_OBSIDIAN_DIR push
   ```

### GitHub Issue (agent or human task)

Create an issue on the appropriate repo:

```bash
gh issue create --repo OWNER/REPO --title "TITLE" --body "BODY" --label "agent-task"
```

- Add `--label "agent-task"` only for tasks the agent should pick up autonomously.
- Omit the label for human tasks.
- If no repo context is obvious, ask the user which repo.

### README.md (repo dev memory)

Append to the dev memory section of the current repo's README.md:

1. Read the existing README.md.
2. Find or create a `## Dev Memory` section.
3. Append the new item with a date prefix: `- **YYYY-MM-DD**: <content>`.
4. Do not commit — leave it staged for the user to review.

### CLAUDE.md (repo agent guidance)

Append to the appropriate section of the current repo's CLAUDE.md:

1. Read the existing CLAUDE.md.
2. Find the most relevant section (conventions, anti-patterns, etc.).
3. Append the new guidance.
4. Do not commit — leave it staged for the user to review.

**Important:** CLAUDE.md and README.md edits are staged but not committed. These files shape agent and human behavior — the user should review before committing.

## Multi-route inputs

Some inputs belong in multiple places. For example:
- "We decided to use PostgreSQL instead of SQLite" → **Memory daily log** (ephemeral record of the decision today) + **CLAUDE.md** (guidance for future agent behavior) + **README.md** (dev memory for humans)
- "Research how to add OAuth" → **GitHub Issue** (task) + **Memory daily log** (captured the intent)

When routing to multiple destinations, execute each route and report what was saved where.

## Output

After routing, confirm with a brief summary:

```
Captured → Memory daily log: "decided to use PostgreSQL over SQLite"
Captured → CLAUDE.md: added PostgreSQL convention to ## Conventions (staged, not committed)
Captured → README.md: added to ## Dev Memory (staged, not committed)
```

## Examples

**User:** "capture: the API rate limit is 100 req/min, we hit it during bulk imports"
→ Route: Durable + Repo-specific + Human → **README.md** dev memory
→ Also: Ephemeral → **Memory daily log**

**User:** "inbox: add retry logic to the webhook handler"
→ Route: Task + Agent → **GitHub Issue** with agent-task label

**User:** "save this: always use uv run, never raw python"
→ Route: Guidance + Repo-specific + Agent → **CLAUDE.md**

**User:** "capture: learned that pydantic v2 changed model_dump from dict()"
→ Route: Durable + Personal + Self → **Obsidian knowledge_graph** atomic note
→ Also: Ephemeral → **Memory daily log**
