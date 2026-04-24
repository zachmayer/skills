---
name: discussion-partners
description: >
  Queries other frontier AI models (GPT-5.5, Gemini 3.1 Pro, Claude Opus)
  for an outside perspective on a hard problem. Use when stuck, spinning
  wheels, want a second opinion, need a code review from another model, or
  sense a blind spot. Trigger phrases: "ask GPT", "get another opinion",
  "second opinion", "what would GPT say", "ask another model", "discussion
  partner". Default: fires all three paths in parallel (background) for
  diverse perspectives. Do NOT use for routine questions Claude can answer
  directly.
allowed-tools: Bash(uv run *), Bash(codex exec *), Task, Write
---

Query other frontier AI models for an outside perspective on a hard problem. One message out, one message back per model — make the context count.

## Default: three models in parallel, all in background

The default invocation fires **all three paths concurrently in the background**, max thinking, latest versions. Diverse opinions from independent models catch blind spots a single model papers over.

| Path | Model | Thinking | Typical wall time |
|------|-------|----------|-------------------|
| **Codex CLI** (`codex exec`) | `gpt-5.5` | xhigh | 5–30 min |
| **`ask_model.py`** | `google-gla:gemini-3.1-pro-preview` | max | ~1–5 min |
| **Task sub-agent** | Claude Opus | adaptive max | ~1–5 min |

**All three run with `run_in_background: true`.** Never foreground the Codex path — the Bash tool's 10 min timeout will SIGKILL it mid-thought at xhigh. Background is the default for the other two as well since their thinking time can approach the timeout.

Synthesize the fast-returning paths (Gemini, Opus) as soon as they land; tell the user Codex is still in flight and surface its output when the notification arrives. Don't block the turn on the slowest model.

**Missing one provider?** If `GOOGLE_API_KEY` or `OPENAI_API_KEY` isn't configured, run the paths that work and note which was skipped. See `troubleshooting.md`.

### Context budget and strengths per path (important)

The three paths have very different capabilities and sweet spots. Brief each one accordingly, and lean into what each does best.

**`ask_model.py` → Gemini 3.1 Pro** — a sealed room with a whiteboard. **Zero tool access, zero context.** Inline everything: code, error traces, type/helper definitions, constraints. Heavy Markdown with fenced code blocks and language tags; unified diffs where applicable. Structure: question at top, code middle, constraints at bottom.
- **Routes to:** isolated algorithmic puzzles, concurrency/state bugs, edge-case enumeration, architectural tear-downs. Deep logical simulation when you have all the code in one place.
- **Routes away from:** "where is X defined" (no grep), fresh library APIs (no web), repo-wide questions (no filesystem).

**Codex CLI → GPT-5.5 xhigh** — workspace sandbox + web search. **Pointers + sharp question beat bulk inlining.**  Prompt structure: `Task / Question / Context / Artifacts / Constraints` in that order. Send file paths, function names, log snippets, failing tests — not entire files.
- **Routes to:** tool-grounded technical judgment. Tracing a bug across multiple files, evaluating whether a proposed fix matches the real codebase, producing concrete alternatives (not just commentary), pressure-testing assumptions with local inspection.
- **Routes away from:** pure text-only asks, rhetoric/messaging, abstract brainstorming.

**Task sub-agent → Claude Opus** — full Claude Code tool access, fresh conversation. **Problem first, ask last.** Two-line TL;DR at top, then details. Pass file paths rather than inlining long files.
- **Routes to:** design/taste calls (naming, boundary placement, whether complexity is earning its keep), long multi-file refactors (1M context), prose artifacts (PR descriptions, API docs, error messages), adversarial self-review of Claude Code output, subtle state/concurrency bugs that pattern-match.
- **Routes away from:** hard math / novel algorithms (GPT wins), fresh-knowledge questions about recent library releases, exhaustive "find-every-bug-in-500-lines" (Gemini's deep-trace wins), pure numeric/statistical reasoning.

**Framing directives that actually matter (all three):**
- "Critique" → adversarial, design-flaw-hunting. "Review" → balanced. "What would you do differently" → constructive alternatives. Pick on purpose.
- "Be direct, skip praise, lead with strongest objections" genuinely improves output quality (especially for Opus, which hedges by default).
- "You are a senior engineer" role prompts are mostly fluff. Skip them.

Write three separate files (e.g. `~/claude/scratch/prompt_{codex,gemini,opus}.md`) tuned per path — not one blob sent three ways.

## Quick-question alternatives (judgment call)

When a full three-way is overkill — a quick sanity check, simple "does this look right", thinking-aloud with one other brain — pick one of these and skip the parallel default:

- **Opus sub-agent** (fastest, least diversity). Same family as you, but different fresh context. Best when the question is localized and you want an immediate outside read.
- **`gpt-5.5 reasoning low` via Codex CLI** (fast, different family). Good for quick OpenAI-side sanity checks.
- **Gemini 3.1 Pro with `-t low`** (fast, different family). Good for quick Google-side sanity checks.

All three are still reasonable to `run_in_background: true`; "quick" here means 30s–2min rather than 10+ min.

## Deep / pro-tier correctness option

For hard correctness problems where max depth beats max speed, **add** `openai-responses:gpt-5.4-pro` via `ask_model.py` — the latest OpenAI pro model currently served by the Responses API. 10–15+ min runtime; **always `run_in_background: true`**. Once OpenAI ships `gpt-5.5-pro` to the API (announced; staged safeguard rollout), the same flag pattern picks it up (`-m openai-responses:gpt-5.5-pro`) — no skill change needed.

## Framing Your Question

Each model you invoke gets **one message out and one response back** — no follow-up. The *Context budget* section above tells you what each path already knows; everything else it needs must be in the prompt.

1. **State what you're stuck on.** "I tried A, B, C and none work because D" — not just "help me with X".
2. **Ask a specific question and set the frame.** What kind of answer do you want: diagnosis, alternative approach, code review, sanity check?
3. **Include all relevant context** (for `ask_model.py`; pointers for Codex / sub-agent). Use the `mental-models` skill to structure your thinking first if the question is fuzzy.
4. **Never include secrets.** API keys, credentials, tokens. Beyond that, the user makes their own judgment calls on what to share externally — the skill doesn't enforce content rules.

Bad: "How do I fix this auth bug?"
Good: "Here is my auth middleware [code]. Users with expired tokens get a 500 instead of 401. I have verified the token validation logic is correct and the error handler is registered. The 500 comes from [stack trace]. What could cause the error handler to be bypassed?"

## Invoking each path

All examples assume prompts have been written to `~/claude/scratch/prompt_*.md`. `SKILL_DIR` is this skill's directory — the absolute path is `/Users/zach/source/skills/.claude/skills/discussion-partners` on this machine; `uv run --directory <that-path>` finds the script and its PEP 723 deps.

### Codex CLI (GPT-5.5)

```bash
# Default: xhigh fast, background. Output written to a file for easy reading.
codex exec --full-auto -m gpt-5.5 -c service_tier="fast" -c model_reasoning_effort="xhigh" \
  -o ~/claude/scratch/codex_output.txt - < ~/claude/scratch/prompt_codex.md

# Quick version: low reasoning for faster return
codex exec --full-auto -m gpt-5.5 -c service_tier="fast" -c model_reasoning_effort="low" \
  -o ~/claude/scratch/codex_output.txt - < ~/claude/scratch/prompt_codex.md

# With web search enabled
codex exec --full-auto --search -m gpt-5.5 -c service_tier="fast" -c model_reasoning_effort="xhigh" \
  -o ~/claude/scratch/codex_output.txt - < ~/claude/scratch/prompt_codex.md
```

Always `run_in_background: true` via the Bash tool. If `-m gpt-5.5` errors with "model does not exist", OpenAI's account-staged rollout hasn't reached you yet — fall back to `-m gpt-5.4`. See `troubleshooting.md`.

### ask_model.py (Gemini / OpenAI pro via Responses API)

```bash
# Gemini 3.1 Pro at max thinking (default — just omit -m)
uv run --directory SKILL_DIR python scripts/ask_model.py -f ~/claude/scratch/prompt_gemini.md

# Gemini low thinking (fast, good for large prompts)
uv run --directory SKILL_DIR python scripts/ask_model.py -t low -f ~/claude/scratch/prompt_gemini.md

# GPT-5.4 Pro via Responses API — latest OpenAI pro available via API today (~10–15 min)
# When 5.5-pro ships to the API, swap to -m openai-responses:gpt-5.5-pro (same flag pattern)
uv run --directory SKILL_DIR python scripts/ask_model.py \
  -m openai-responses:gpt-5.4-pro -f ~/claude/scratch/prompt_pro.md
```

Always `run_in_background: true`. Thinking effort is auto-set to max per provider; `-t low` overrides for speed.

### Task sub-agent (Opus)

```
Task(
  subagent_type="general-purpose",
  description="Discussion partner review",
  prompt="<question + file paths + what you've tried>"
)
```

Per `~/CLAUDE.md`, sub-agents default to Opus in this environment. The sub-agent gets **fresh context** — only what you pass in `prompt=`. But it has full tool access (Read, Grep, Glob, Bash), so file paths + a question beats inlining code.

`run_in_background: true` here too; the sub-agent may take several minutes on a thorough review.

## `ask_model.py` options

- `--model` / `-m`: Full pydantic-ai model string (default: `google-gla:gemini-3.1-pro-preview`)
- `--thinking` / `-t`: Override thinking level. Gemini: `low`/`high` (default: max). OpenAI: `low`/`medium`/`high`/`xhigh` (default: `xhigh`).
- `--system` / `-s`: Optional system prompt override
- `--file` / `-f`: Read question from a file (use for long prompts — avoids shell-escape traps)
- `--list-models` / `-l PREFIX`: List known model names filtered by prefix (e.g. `-l google-gla` or `-l ""` for all). Note: only prints pydantic-ai `KnownModelName` entries; `openai-responses:*` strings aren't listed but still work.

## Multiple calls

Each invocation gets zero context from previous calls. For follow-ups, include the prior exchange in the new prompt: "I asked X, you answered Y, help me understand Z."

## Setup and troubleshooting

- **If a path isn't installed/configured:** see `setup.md`.
- **If a path errors** (`model_not_found`, `insufficient_quota`, `invalid_api_key`, etc.): see `troubleshooting.md`.
