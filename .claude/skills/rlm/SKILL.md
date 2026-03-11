---
name: rlm
description: >
  Analyze large context (100K+ tokens) using phased reasoning with tool-based
  filtering and sub-agent delegation. Based on the RLM paper (arXiv:2512.24601).
  Use when working with large files, long transcripts, massive codebases, or any
  context too large to reason about in a single pass. Do NOT use for small files,
  simple lookups, or tasks where the full context fits comfortably in working memory.
---

# RLM: Recursive Language Model Protocol

Core principle: **Tools filter, sub-agents reason.**

Use deterministic tools (Read, Grep, Glob, Bash) to FILTER and NARROW context. Use sub-agents (Task tool) to REASON about filtered content. Never try to reason about the entire large context at once.

## Phase 1: Recon

Always start here. Understand the data shape before analyzing.

1. **Measure**: File sizes, line counts, format detection
2. **Identify structure**: Headers, sections, delimiters, record boundaries
3. **Plan chunking**: Based on actual document structure — NOT arbitrary byte offsets

Chunk by semantic boundaries (section headers, message delimiters, function definitions, blank-line-separated blocks). Structure-aware chunks preserve meaning; arbitrary splits destroy it.

Example recon:
```bash
wc -l large_file.txt
head -100 large_file.txt
```
Then use Grep to find section boundaries (e.g., `^##`, `^class `, `^def `, delimiter patterns).

## Phase 2: Filter + Analyze

Iterate until you have enough information:

1. **Filter with tools**: Grep for relevant sections, Read specific line ranges, Glob for matching files
2. **Delegate to sub-agents**: Send substantial filtered chunks + focused questions to Task agents
3. **Track findings**: Store results mentally — never re-read files you already processed

Rules:
- **Substantial chunks**: 5-10 focused sub-agent queries, not dozens of tiny ones. Sub-agents handle large inputs well — feed them 10K-50K chars each
- **Specific questions**: "What authentication methods does this module use?" not "Analyze this code"
- **Parallel where possible**: Launch independent Task calls simultaneously
- **No repeated work**: If you already know the answer from Phase 1, don't re-query

## Phase 3: Synthesize

1. Review all sub-agent results
2. Identify patterns, conflicts, and gaps
3. If gaps remain, run targeted Phase 2 follow-ups
4. Produce final answer

## Tool Selection

| Need | Tool | Why |
|:-----|:-----|:----|
| Find files by pattern | Glob | Fast file discovery |
| Find content by pattern | Grep | Deterministic filtering — narrows search space |
| Read specific sections | Read (with offset/limit) | Avoids loading entire large files |
| Data transforms | Bash (wc, sort, awk) | Deterministic analysis |
| Semantic reasoning | Task (sub-agents) | Delegate understanding of filtered chunks |

## Anti-Patterns

- **Reading entire large files into context.** Use Read with line ranges after Grep identifies relevant sections.
- **Vague sub-agent prompts.** Always include: what the chunk contains, what specific question to answer, what format to return.
- **Over-decomposition.** 50 tiny queries waste budget and lose coherence. Prefer fewer, meatier queries.
- **Skipping recon.** Jumping to analysis without understanding data shape leads to bad chunking and missed sections.
- **Re-reading processed content.** Track what you've learned. Build on prior iterations.
