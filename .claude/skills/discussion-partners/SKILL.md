---
name: discussion-partners
description: >
  Queries other frontier AI models (GPT-5.5, Gemini 3.1 Pro, Claude Opus)
  for an outside perspective on a hard problem. Use when stuck, spinning
  wheels, want a second opinion, need a code review from another model, or
  sense a blind spot. Trigger phrases: "ask GPT", "get another opinion",
  "second opinion", "what would GPT say", "ask another model", "discussion
  partner". Do NOT use for routine questions Claude can answer directly.
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

**All three run with `run_in_background: true`.** Never foreground any path — Codex at xhigh will SIGKILL at the Bash tool's 10 min timeout, and the other two can approach or exceed that too.

Synthesize the fast-returning paths (Gemini, Opus) as soon as they land; tell the user Codex is still in flight. **But do wait for all three before advancing to the next phase of work** — the whole point of three-way review is the diversity of opinion. Don't ship a change or move on until you've heard from all three. "Don't block the turn" ≠ "don't wait at all"; it means surface partial results so the user isn't staring at a blank screen for 20 minutes.

**Missing one provider?** If `GOOGLE_API_KEY` or `OPENAI_API_KEY` isn't configured, run the paths that work and note which was skipped. See `troubleshooting.md`.

### Build one shared context + thin per-path framing

**All three models should see the same problem, same code, same evidence, same question.** That's the whole point of three-way review — if one gets a thinner prompt, they're not running the same race. Don't undercontext one to play to another's strengths.

The shape:

1. **Write a single `context.md`** with everything needed to answer: problem statement, the actual question, relevant code inline (fenced blocks, unified diffs for changes), error traces verbatim, repro steps, constraints, what you've already tried and rejected with reasons. Heavy Markdown — it parses cleanly for all three.
2. **Per-path prompt files reference or inline `context.md`** plus a thin framing header tuned to each path:
   - **`prompt_gemini.md`** = the full context inlined. Gemini has no tools — if it's not in the prompt, Gemini can't see it.
   - **`prompt_codex.md`** = the full context, plus "feel free to inspect the repo at `<abs-path>` to verify or cross-reference." Codex has workspace tools + web search; pointers let it verify rather than argue from the prompt.
   - **`prompt_opus.md`** = the full context, plus file paths to read if helpful: `<paths>`. Opus has full Claude Code tool access and fresh conversation context — give it the same blob as the others, let it fetch more if needed.

That way each model gets a fair shot, and the two with tools can verify/extend without being starved.

### Routing and strengths per path

When a full three-way is warranted, send to all three. Use these notes to tune the framing header and to decide quick-question alternatives (below).

**`ask_model.py` → Gemini 3.1 Pro** — sealed room with a whiteboard. No tools, max thinking.
- **Strong at:** isolated algorithmic puzzles, concurrency/state bugs, edge-case enumeration, architectural tear-downs, deep logical simulation when the code fits in the prompt.
- **Weak at:** anything requiring lookup ("where is X defined", recent library APIs, repo-wide questions). It will hallucinate rather than admit it can't see.

**Codex CLI → GPT-5.5 xhigh** — workspace sandbox + web search + 1M context.
- **Strong at:** tool-grounded technical judgment — tracing a bug across files, evaluating a fix against the real codebase, producing concrete verified alternatives, pressure-testing assumptions with local inspection.
- **Weak at:** pure rhetoric / abstract brainstorming with no artifacts to ground on.

**Task sub-agent → Claude Opus** — full Claude Code tool access, fresh conversation, 1M context.
- **Strong at:** design/taste calls (naming, boundary placement, whether complexity is earning its keep), prose artifacts (PR descriptions, API docs), adversarial self-review of Claude Code output, subtle state/concurrency patterns.
- **Weak at:** hard math / novel algorithms (GPT wins), exhaustive "find-every-bug-in-500-lines" (Gemini's deep-trace wins).

**Large multi-file refactors:** both Codex and Opus have 1M context and can read the workspace — either works. If firing both, split the surface explicitly ("Codex: focus on module A. Opus: focus on module B.") so they don't step on each other.

### Framing directives

- **"Critique"** → adversarial, design-flaw-hunting. **"Review"** → balanced. **"What would you do differently"** → constructive alternatives. Pick on purpose.
- **"Be direct, skip praise, lead with strongest objections. If you have no objections, say so — LGTM is a fine answer."** This works (especially on Opus, which hedges by default) *and* it prevents anti-sycophancy from manufacturing concerns where none exist. You want calibrated honesty, not forced objection.
- **"You are a senior engineer" role prompts** — fluff at this capability level. Skip.
- **Watch for leading the witness.** Present evidence and ask the question; don't state your hypothesis as a conclusion the model should validate. Scout mindset: what are you trying to find out, not prove? If you already believe the bug is in `auth.py`, saying so anchors all three models. Ask what *could* cause the observed behavior and let them find it independently.

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
3. **Include all relevant context** — the full shared context, as described above. Use the `mental-models` skill to structure your thinking before writing the prompt if the question is fuzzy.
4. **Never include secrets.** API keys, credentials, tokens. Beyond that, the user makes their own judgment calls on what to share externally — the skill doesn't enforce content rules.

Bad: "How do I fix this auth bug?"
Good: "Here is my auth middleware [code]. Users with expired tokens get a 500 instead of 401. I have verified the token validation logic is correct and the error handler is registered. The 500 comes from [stack trace]. What could cause the error handler to be bypassed?"

## Invoking each path

Examples assume prompts are at `~/claude/scratch/prompt_{codex,gemini,opus}.md` and `context.md`. `SKILL_DIR` is this skill's directory — resolve to its absolute path via Claude Code's skill location (see MEMORY.md for the current machine's path).

**Before writing**: `~/claude/scratch/` is shared; if files from a prior run exist they'll be overwritten. Either accept that (fine for a fresh three-way) or use unique suffixes (`_$(date +%s)`) when two reviews are in flight concurrently.

**While running**: the Codex `-o` output file is populated as Codex streams. You can `Read` it mid-run to peek at partial output — useful if Codex takes 20+ min and you want to know if it's on-track. Task sub-agent output is opaque until completion.

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

Always `run_in_background: true` via the Bash tool. See `troubleshooting.md` for error handling.

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
