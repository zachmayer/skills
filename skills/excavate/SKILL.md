---
name: excavate
description: excavate performs assumption archaeology. it reveals the layered structure of "what must be true" beneath a claim, plan, belief, or principle. the goal is to surface implicit premises, map dependencies, identify cruxes, and expose where disagreement or uncertainty actually lives. unlike antithesize (generating opposition), excavate is diagnostic. it lights up the skeleton beneath the stance.
---

## tl;dr

**excavate** maps the assumption-stack that makes the claim coherent.

> "what hidden assumptions are propping this up, and what do *those* depend on?"

it's a **downward-mapping operator**.

---

## when to use

use **excavate** when you want to understand:

- the **hidden structure** under a belief or plan
- the **real cruxes** driving disagreement
- what assumptions are **empirical** vs **normative** vs **structural**
- where uncertainty actually lives

don't use when you want opposition — use **antithesize**.

rule of thumb: **excavate = "what must be true beneath this?"**

---

## assumption types (tags)

- **[empirical]** — descriptive world claims, probabilities, causal expectations
- **[normative]** — value judgments, priorities, ethical constraints
- **[structural]** — incentives, institutions, competitive dynamics, coordination structure
- **[psychological]** — assumptions about cognition, motivation, bias, perception
- **[definitional]** — category boundaries, ontology, what terms *mean*

---

## signature

excavate(claim, max_depth?, focus?) → {assumption_tree, cruxes, probes}

- **claim:** the surface statement to dig into
- **max_depth:** default 3–4; deeper exposes more layers
- **focus:** optional (empirical | normative | structural | psychological | definitional)

output is:

- a **layered assumption tree**
- a **crux list** (3–7 load-bearing assumptions)
- **probe questions** that would most update the stance

---

## process

### step 0: normalize the claim
ensure the claim is crisp, scoped, and not two claims fused together.

### step 1: generate layer-1 assumptions
ask: "what must be true for this claim to make sense?"
produce 3–7 assumptions, each tagged by type.

### step 2: recurse
for each assumption: "and what must be true for *that* to make sense?"
produce 1–4 sub-assumptions until hitting a value-axiom, redundancy, or max_depth.

### step 3: tag flags
mark assumptions with:

- **[CRUX]** — flipping this would flip or materially change the claim
- **[HIGH-UNCERTAINTY]** — evidence weak or unknown
- **[HIGH-LEVERAGE]** — clarifying this resolves multiple branches

### step 4: summarize cruxes
select the 3–7 highest-impact assumptions based on crux x uncertainty x leverage.

### step 5: generate probes
produce concrete questions or tests that would update the cruxes.

---

## quality criteria

- layers are clean, no duplicated logic; tags correctly classify types
- 3–7 assumptions marked as genuine load-bearing cruxes
- surfaces where actual disagreement likely lives
- distinguishes empirical uncertainty from value conflict
- each probe targets a crux and is measurable or investigable

---

## anti-patterns

- **shallow paraphrase** — restating the claim in different words is not excavation
- **circular layers** — each lower layer must add new structure, not repeat the parent
- **overproduction** — 20+ assumptions per layer loses coherence
- **premature judgment** — excavate is descriptive, not evaluative

---

## integration with other ops

- **antithesize** → generate structured opposition from surfaced assumptions
- **dimensionalize** → transform cruxes into measurable dimensions for comparison

---

## meta-note

excavate = **assumption topology**.

the output isn't a verdict — it's the *map* that tells you where effort, evidence, or disagreement should go next.

For worked examples and detailed layer types, see [REFERENCE.md](REFERENCE.md).
