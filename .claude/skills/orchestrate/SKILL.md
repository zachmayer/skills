---
name: orchestrate
description: >
  Orchestration: decompose a task into a dependency graph of sub-tasks, spawn
  specialized sub-agents in parallel where possible, and aggregate results.
  Use when a task has 3+ independent or dependent sub-tasks that benefit from
  parallel execution or specialized agent routing. Do NOT use for simple
  sequential tasks, single-agent work, or when ralph_loop is a better fit
  (iterative development with commits).
---

You are a coordinator agent. Your job is to decompose $ARGUMENTS into a directed acyclic graph (DAG) of sub-tasks, route each to the right sub-agent type, execute them respecting dependencies, and aggregate the results.

Also apply these skills as needed:
- `ultra_think` for complex decomposition decisions
- `staff_engineer` for engineering rigor
- `ask_questions` if the task is ambiguous — clarify before decomposing

## Agent Routing Guide

Choose the right sub-agent type for each sub-task:

| Agent type | Route when... |
|------------|---------------|
| `Explore` | Finding files, searching code, understanding structure — read-only |
| `Bash` | Running commands, builds, tests, git operations |
| `Plan` | Designing architecture, planning implementation strategy |
| `general-purpose` | Multi-step work requiring read + write + search + commands |

## Phase 1: Decompose

Analyze the task and break it into sub-tasks. Each sub-task needs:

| Field | Description |
|-------|-------------|
| `id` | Short identifier (e.g. `research-api`, `impl-schema`, `write-tests`) |
| `title` | What this sub-task accomplishes |
| `agent` | Sub-agent type from the routing guide above |
| `depends_on` | List of task IDs that must complete before this one starts |
| `prompt` | Complete, self-contained prompt for the sub-agent |

### Decomposition rules

1. **Self-contained prompts.** Each sub-agent starts with zero context. Its prompt must include everything it needs: file paths, function names, constraints, expected output format. Never assume the sub-agent can see your conversation.
2. **Minimize dependencies.** Flatten the DAG. If two tasks don't actually depend on each other, don't chain them. More parallelism = faster completion.
3. **Right-size tasks.** Each sub-task should complete in one agent invocation. If it's too big, split it. If it's trivial, merge it with an adjacent task.
4. **Explicit outputs.** Tell each sub-agent exactly what to return: a file path, a summary, a list, a decision. Vague prompts produce vague results.

Output the DAG as a fenced JSON block for the user to review:

```json
{
  "goal": "High-level description of the coordinated task",
  "tasks": [
    {
      "id": "research-api",
      "title": "Find all API endpoint definitions",
      "agent": "Explore",
      "depends_on": [],
      "prompt": "Find all files defining HTTP API endpoints in the codebase..."
    },
    {
      "id": "impl-validation",
      "title": "Add input validation to endpoints",
      "agent": "general-purpose",
      "depends_on": ["research-api"],
      "prompt": "Given these API endpoints: [RESULTS FROM research-api]..."
    }
  ]
}
```

## Phase 2: Validate the DAG

Before executing, verify:

1. **No cycles.** The dependency graph must be a DAG. If A depends on B and B depends on A, restructure.
2. **No orphan dependencies.** Every ID in `depends_on` must exist as a task `id`.
3. **Reachable roots.** At least one task has `depends_on: []` — otherwise nothing can start.
4. **Prompt completeness.** Each prompt is self-contained. A sub-agent reading only its prompt should know exactly what to do.

If the task is complex or ambiguous, show the DAG to the user and wait for approval before executing. For straightforward decompositions, proceed directly.

## Phase 3: Execute

Process the DAG in topological order:

1. **Identify the ready set** — all tasks whose dependencies are satisfied (completed or have no dependencies).
2. **Launch ready tasks in parallel** using the Task tool. Use `description` for the task title and `subagent_type` matching the `agent` field.
3. **Collect results.** When a task completes, store its result keyed by task ID.
4. **Inject results into dependents.** Before launching a dependent task, manually substitute the results from completed upstream tasks into the dependent's prompt. Write the actual data inline — sub-agents cannot access prior results automatically.
5. **Track progress.** Use `TodoWrite` to register sub-tasks and update their status (`in_progress` → `completed`) as they execute.
6. **Repeat** until all tasks are complete or a task fails.

### Handling failures

- If a sub-agent fails or returns an unusable result, **do not skip its dependents**. Instead:
  1. Diagnose what went wrong from the sub-agent's output.
  2. Rewrite the prompt addressing the failure (more context, different approach, narrower scope).
  3. Retry once. If it fails again, report the failure to the user with the sub-agent's output and ask how to proceed.
- Never silently drop a failed task — its dependents are blocked and the user needs to know.

### Execution constraints

- **Maximum 5 parallel sub-agents.** More than this overwhelms context tracking.
- **No nested coordination.** Sub-agents should not invoke the coordinator skill themselves. Keep the tree one level deep.
- **Background agents for slow tasks.** Use `run_in_background: true` for tasks expected to take more than 30 seconds, then check on them with the Read tool.

## Phase 4: Aggregate

Once all tasks complete:

1. **Collect all results** into a structured summary.
2. **Check for consistency** — do results from independent branches contradict each other? Flag conflicts.
3. **Synthesize** a final answer or deliverable from the combined results.
4. **Report** to the user:
   - What was accomplished (per task)
   - Any failures or retries
   - The synthesized result
   - Suggested next steps if applicable

## When NOT to coordinate

Not every multi-step task needs a coordinator. Skip this skill when:

- **Tasks are purely sequential** with no parallelism opportunity → just do them in order
- **It's iterative development** → use `ralph_loop` instead
- **There are fewer than 3 sub-tasks** → overhead of coordination exceeds benefit
- **All tasks need the same agent type** → batch them or do them sequentially
- **The task requires tight feedback loops** between steps → coordination adds latency

The coordinator adds value when there are **independent workstreams that can run in parallel** and **dependency edges that need to be respected**. If neither applies, don't use it.
