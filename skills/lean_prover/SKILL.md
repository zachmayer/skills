---
name: lean_prover
description: >
  Multi-agent Lean 4 theorem proving system using blueprint-driven coordination.
  Use when proving Lean 4 theorems, formalizing math, working through Mathlib
  proofs, or tackling competition problems (Putnam, IMO, MiniF2F). Also use when
  orchestrating complex proof campaigns across multiple lemmas.
  Do NOT use for general programming, non-Lean math, or single-tactic proofs that
  need no orchestration.
---

Prove Lean 4 theorems using a multi-agent coordinator pattern with blueprint-driven dependency tracking and systematic exploration. Extracted from [numina-lean-agent](https://github.com/project-numina/numina-lean-agent), which proved all 12 Putnam 2025 problems.

## Architecture

Four specialized agent roles, all launched via the Task tool:

| Agent | Role | When to spawn |
|-------|------|---------------|
| **Coordinator** | Reads blueprint, selects targets, delegates. NEVER proves directly. | Always (you are this) |
| **Blueprint Agent** | Consults external AI for proof strategies, splits complex lemmas | Unclear informal proof, attempts exhausted (>40/50) |
| **Sketch Agent** | Formalizes informal statements into Lean, adds status comments | Statement not yet in Lean |
| **Proof Agent** | Systematically proves a single lemma with budget-based exploration | Formalized lemma ready for proof |

**Orchestration flows:**
- Simple (formalized, clear): Proof Agent
- Medium (needs formalization): Sketch Agent -> Proof Agent
- Complex (unclear/stuck): Blueprint Agent -> Sketch Agent -> Proof Agent

## Blueprint

Maintain a `BLUEPRINT.md` as the single source of truth. Order by dependency topology (dependencies before dependents). Update IMMEDIATELY after any progress.

```markdown
# [type] [label]
## meta
- **label**: [lem:foo]
- **uses**: [[def:bar], [lem:baz]]
- **file**: `Path.lean:42` or (to be created)
- **status**: done | partial | todo
- **attempts**: 14 / 20
## statement
[Informal statement]
## proof
[Detailed informal proof - fill BEFORE formalization]
```

**Target selection**: Only pick items where all `uses` dependencies are `done`. Prefer `partial` over `todo` (resume work). Follow priority order.

## Proof Agent Protocol

The core execution engine. Each proof agent session focuses on ONE lemma.

### Budget system

| Proof size | Min attempts | Categories required |
|-----------|-------------|-------------------|
| <5 lines | 20 | 3 of 5 |
| 5-20 lines | 35 | 4 of 5 |
| >20 lines | 50 | All 5 |

### Five method categories (must try each)

1. **Library Search**: leandex -> loogle -> local_search. ALWAYS search before proving.
2. **Direct Tactics**: `hint` first, then `grind`, then specific tactics (`omega`, `simp`, `aesop`, `ring`, `linarith`, `norm_num`).
3. **Structural**: induction, cases, contradiction, contrapositive.
4. **Term Mode**: direct proof construction with `exact`, `fun`, existence witnesses.
5. **Decomposition**: `have`/`suffices` for intermediate goals, extract helper lemmas with `sorry`.

### Core philosophy

Reduce goals until automation (`hint`/`simp`/`grind`/`omega`/`aesop`) finishes them. Transform with `intro`/`unfold`/`rw`/`have`/`suffices`, then try automation again. Repeat.

### External consultation checkpoints (mandatory)

Consult an external model via the `discussion_partners` skill at these attempt counts:
- **0**: Before ANY code - get strategy, insights, mathlib suggestions
- **2**: Early guidance after first attempts
- **4**: Alternative approaches
- **8**: Decomposition ideas
- **16**: Library search assistance
- **32**: Optimization/simplification

### Tmp file workflow

1. Update original file's status comment with `tmp file: tmp_<lemma>.lean`
2. Create tmp file in same directory, import original
3. Do ALL proof attempts in tmp file
4. Copy back when proven, delete tmp file

## Key Rules

### No axioms, only sorry
- `axiom` invalidates proofs. ALWAYS use `sorry` instead.
- Leave only the SMALLEST stuck part as sorry. Everything else must be proven.
- Code MUST compile cleanly (no severity-1 errors) before exiting.

### No brute-force enumeration
- Do NOT use `decide`/`fin_cases`/`interval_cases` to enumerate cases without checking for a general proof first.
- Consult external AI before any enumeration approach.
- Prefer induction, WLOG, contradiction over case explosion.

### Status comments on every lemma
```lean
/- (by claude)
State: 🔄 partial
Attempts: 12 / 20
tmp file: tmp_foo.lean
-/
lemma foo : P := by sorry
```

### Lean tips
- NEVER use `lake build` — use `lean_diagnostic_messages` for verification
- ALWAYS specify types on fractions: `((2 : ℝ) / 3)` not `(2 / 3)`
- AVOID natural number division/subtraction unless required by theorem statement
- If `decide` times out, write symbolic proof instead of increasing `maxHeartbeats`
- If a proof exceeds 500 lines, extract helper lemmas

## Splitting Protocol (Blueprint Agent)

When a lemma is too complex or attempts exhausted:
1. Consult external AI for detailed step-by-step informal proof
2. If proof has 3+ distinct steps -> SPLIT into sub-lemmas
3. Create sub-lemma entries in blueprint with dependencies
4. Update original lemma to depend on final sub-lemma
5. Reset original's attempt counter

## Session End Format

Every agent session must end with exactly one line:
```
END_REASON:COMPLETE        # All sorries proven
END_REASON:SELECTED_TARGET_COMPLETE  # This lemma done, others remain
END_REASON:LIMIT           # Budget exhausted or stuck
```
