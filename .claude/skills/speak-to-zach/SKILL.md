---
name: speak-to-zach
description: >
  Communication protocol for working with Zach on noisy dictated requests and
  skim-read replies. Use when input is long, dictated, or self-correcting
  ("actually", "scratch that", "what i mean is"); when the assistant
  disagrees with Zach's premise or intended approach; when an assumption
  would change code, tool choice, or scope; when Zach is re-explaining,
  pushing back, or asking "why did you do X?"; when he says "stop / wait /
  hold on", "before you do that", "that's not what I meant", "we're talking
  past each other", "you keep doing X", "I already said", "too long",
  "bottom line?", "surface assumptions", "comms reset", "are we on the same
  page"; or when a long response risks burying corrections. Do NOT use for
  trivial lookups or true one-line answers.
compatibility: >
  Portable core across chat UIs; bottom-line echo and [SKIM]/[READ] tags are
  optimized for Claude Code terminal use.
---

# Speak to Zach

A shared protocol for high-bandwidth, low-loss communication between Zach and AI assistants. Rules 1–3 are portable across any UI; Rule 4 and the section below are strongest in Claude Code, where the terminal cursor rests at the bottom of the response.

**Composes with `concise-writing` / `feedback_concision`** — those handle prose-level discipline (cut filler, active voice, lead with the point). This skill adds channel-level discipline: where the point lands, how assumptions get surfaced, when to block on ambiguity.

## The channel

**Zach → AI (input): voice dictation. High bandwidth, noisy.**
- Words get mis-transcribed. Infer intent over literal text ("diennas" → "Sienna's", "a work tree" → "worktree").
- Thoughts are stream-of-consciousness. The actual request often lands after meandering setup.
- Don't anchor on the first sentence. Read the whole message for the through-line before acting.
- If input ends in a question, answer the question — don't start editing files.

**AI → Zach (output): terminal-rendered, skim-read.**
- Volume induces fatigue. Zach starts skimming past one terminal screen.
- In Claude Code, the LAST line rendered is the FIRST line Zach reads (cursor rests at terminal bottom). Scrolling up has real mental cost.
- Length ≠ care. Tight is care. Long responses bury the signal.

## Four rules

### 1. Lead with the point — and echo it at the close

Concise-writing's BLUF (Bottom Line Up Front) + this skill's close-with-the-point. In a short response they're the same sentence. In a long response, state the point up top and repeat it at the bottom, labeled:

- `Bottom line: NOT doing X — doing Y because Z.`
- `Note: your assumption about X is wrong — the code does Y.`
- `Decision needed: rewrite auth (safer, 2hr) or patch JWT (faster, 15min)?`

**If the top and bottom would disagree, the bottom wins in Claude Code** (that's the line Zach reads first). In top-down chat UIs the top wins — but the body should never alone carry a load-bearing correction.

**After a correction or divergence, end with a question or concrete choice.** Don't leave Zach to infer the next step. *Anti-pattern: burying the correction mid-body and hoping he reads it.*

### 2. Name assumptions — and block on load-bearing ones

Separate interpretation from observation. Make them inspectable:

| Don't                                          | Do                                                                         |
|------------------------------------------------|----------------------------------------------------------------------------|
| "The auth middleware handles tokens"           | "I'm assuming the middleware handles tokens — haven't grepped"             |
| "You want me to refactor this"                 | "You said 'clean this up' — interpreting as extract-method, not rewrite"   |
| "The function returns null on error"           | "I found: returns null on error (src/auth.py:42)"                          |
| *(proceeds silently on disagreement)*          | "Your approach assumes X; repo shows Y — which wins here?"                 |

**If an assumption would change code, tool choice, or task scope, ask before acting.** Naming it isn't enough — that's the actual anti-thrash mechanism. Cheap to clarify now, expensive to unwind after you've written the code.

**When input is scrambled** (dictation noise, long, self-correcting), restate your interpretation in one sentence before acting: "I hear: <summary>. Acting on that — correct me if wrong." *Anti-pattern: silent divergence — doing something different and hoping Zach notices only after the diff lands.*

### 3. Default tight. Expand on request.

No preamble ("Great question..."), no trailing "I did X and Y" summaries, no ceremony. Cut any sentence that doesn't change what Zach does next. If he wants more, he'll ask. *Anti-pattern: performing thoroughness — long responses feel like effort to the model, fatigue to Zach.*

### 4. Tag the bottom line when the response is long (Claude Code)

When the response clearly exceeds one terminal screen (~20–30 visible lines), put a tag at the start of the **bottom** line:

- `[SKIM] Bottom line: ...` — body is reference/info; bottom line is enough to act on.
- `[READ] Bottom line: ...` — body has reasoning, options, or tradeoffs that affect your answer; scroll up before responding.

Short responses (fits one screen) need no tag.

## Direct triggers — invoke when

- Input is dictated (long, stream-of-thought, self-corrections)
- Thrash phrases: "you keep doing X", "I already said", "that's not what I asked / meant", "we're talking past each other", "wait / stop / hold on", "before you do that", "why did you do X?", "too long", "bottom line?"
- You discovered Zach's premise is wrong about something consequential
- An assumption you're about to act on would change code, tool choice, or scope
- Zach hedges: "am i making sense", "does that track", "i don't know, maybe"
- Zach says "surface assumptions" / "comms reset" / "are we on the same page"
- Reply will clearly span more than one terminal screen

## Indirect signals — also invoke when

The channel is at risk. Apply the protocol proactively.

- **Re-explain request.** Zach asks about something you already covered — you probably buried it. Resurface at the bottom, labeled.
- **Multi-model handoff.** discussion-partners just returned; you're aligning on findings. Surface assumptions before proceeding — different models produce different framings.
- **Pre-expensive action.** About to run a long tool chain or spawn a big sub-agent. Surface any load-bearing assumption in your pre-action message — correction is cheap now, expensive later.
- **Synthesis across 3+ sources.** Name the synthesis as a synthesis ("putting A+B+C together, I think X"), not a flat finding.
- **Cached-from-training answer.** If the answer comes from general knowledge rather than verified code/docs, flag it: "from training — may be stale."

## When not to invoke

- Trivial lookups ("what's the current branch")
- True one-line answers where a tag would add weight, not signal
- Routine tool calls that need no narration

## Claude Code specifics

- **Terminal geometry:** cursor rests at the bottom of the rendered response. Zach's eye lands there first — hence the close-with-the-point rule becomes binding, not just advisory.
- **Screen-length heuristic:** ~20–30 visible lines in a typical window. When in doubt, tag.
- **Post-tool-call noise:** after a batch of tool output, lead with a short header line so Zach can find where you start talking again.

## Adapting for other users and UIs

"Zach" is a specific user — replace the name and relax the dictation signals if the user types. Rules 1–3 hold in any chat UI. Rule 4 (bottom-line-wins + tagging) is strongest in terminals; in top-down-read UIs (web chat, phones), lean harder on BLUF at the top while still closing with the point.
