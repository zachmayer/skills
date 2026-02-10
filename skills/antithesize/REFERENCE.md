# antithesize — reference

Full taxonomy, worked examples, and detailed move descriptions. See [SKILL.md](SKILL.md) for the core pattern and process.

-----

## antithesis types (full menu)

different moves exert different kinds of pressure. pick based on what you're trying to accomplish.

### **refutation** (logical negation)

**what**: show ¬p, contradiction, counterexample, or reductio
**when**: you want falsification pressure, truth-testing
**example**: "thesis claims remote work cuts productivity. panel data with instrumented shocks shows no drop."

### **rival thesis** (coherent alternative)

**what**: full counter-model with different primitives/priors that fits data better
**when**: you want replacement, not just teardown
**example**: "preference isn't discovered—it's regime-generated. constraints create wants, not hide them."

### **objective flip** (same facts, different loss)

**what**: optimize recall not precision; CVaR not mean; latency not throughput
**when**: misalignment is about goals, not facts
**example**: "if objective = retention or female participation, remote work strictly dominates in-office."

### **axis shift** (orthogonalization)

**what**: change the question, hold the answer fixed; challenge relevance, not truth
**when**: you want to escape frame-lock
**example**: "sure bigger models win on capability. but for reliability/compliance, alignment infrastructure compounds faster."

### **causal inversion**

**what**: reverse arrows or condition on different node ("you've mistaken effect for cause")
**when**: the causal story smells post-hoc
**example**: "success didn't cause the strategy—survivors retroactively claim the strategy caused success."

### **role/quantifier swap**

**what**: swap ∀/∃, min/max, buyer/seller, regulator/regulated
**when**: edge-case ambushes, exposing hidden quantifiers
**example**: "works for SOME users" ≠ "works for ALL users"

### **boundary/limit case**

**what**: test at extremes or degenerate regimes (n→∞, liquidity→0, adversary→adaptive)
**when**: exposing hidden assumptions, scale behavior
**example**: "your coordination mechanism works at n=10. at n=1000, it collapses due to gossip overhead."

### **adversarial example** (stress test)

**what**: craft worst-case inputs that satisfy constraints yet violate intent
**when**: robustness audits, red-teaming
**example**: "your content filter passes benign test cases but fails on unicode edge cases adversary will exploit."

### **duality/reparameterization**

**what**: express same system in dual space (primal/dual, time/frequency, price/quantity)
**when**: seeing conserved quantities, alternative formulations
**example**: "in tooling market, stable abstractions are scarce capital; model scale is commodity. dual of capability race."

### **selection/measurement critique**

**what**: attack the pipeline (sampling, survivorship, goodharting, leakage)
**when**: results look "too clean," external validity suspect
**example**: "capability evals cherry-pick leaderboards optimized by scale. selection bias."

### **axiological inversion**

**what**: reorder values (equity > efficiency instead of vice versa), see if policy survives
**when**: norm conflicts, value disagreements
**example**: "optimizing for average hides tail suffering. if you weight equity, opposite policy."

### **phenomenological counter**

**what**: lived-experience report that map misses ("your 'average' erases tails; i live in a tail")
**when**: locating aleatoric vs epistemic error, representation failures
**example**: "your model says garden leave is recovery. but it FEELS like generating new preferences under new regime."

### **performative/strategic mirror**

**what**: "if we make your claim common knowledge, equilibrium shifts (reflexivity)"
**when**: second-order effects, strategy-proofness
**example**: "publishing 'SAT predicts success' makes everyone optimize SAT, destroying the signal."

### **null model / ablation**

**what**: "a dumb baseline does as well; your gears add no marginal evidence"
**when**: puncturing ornamentation, checking necessity
**example**: "your 12-step framework performs same as 'just try stuff and see.' mechanisms are cosplay."

### **foil/negative space**

**what**: delineate what thesis DOESN'T say to reveal scope errors
**when**: deconfusing, clarifying boundaries
**example**: "you claim X helps decision-making. but you never specify WHICH decisions, at WHAT stakes."

-----

## picking the right antithesis type

**fast heuristics by purpose:**

|your goal                                  |use these moves                                                 |
|-------------------------------------------|----------------------------------------------------------------|
|truth pressure (is this even true?)        |refutation, counterexample, selection critique                  |
|better model (what's the right story?)     |rival thesis, causal inversion, reparameterization              |
|robustness (will this break?)              |adversarial example, boundary case, objective flip to worst-case|
|value clarity (what should we optimize?)   |axiological inversion, performative mirror                      |
|reframe (are we asking the right question?)|axis shift, phenomenological counter, foil                      |

**generators** (concrete ways to mint antithesis):

- flip the sign (benefit ↔ harm), timeframe (short ↔ long), or unit of analysis (individual ↔ system)
- swap the objective (mean → tail; accuracy → calibration; growth → resilience)
- invert causality (B causes A), roles (principal ↔ agent), or quantifiers (∀ → ∃)
- push to limits (resource → 0/∞; noise → 0/∞; adversary → adaptive)
- re-express via dual (Lagrangian, Fourier, supply ↔ demand)
- ablate one gear; if predictions don't move, that gear was cosplay

-----

## genre-specific patterns (for rival thesis)

these patterns apply specifically to RIVAL THESIS type. other antithesis types may not need genre-specific structure.

### **review / recommendation**

**thesis**: "X is good, i recommend it"

**antithesis structure**:

- ACCEPT: the experience/facts (what happened)
- FLIP: the evaluation (good → bad, feature → bug)
- REVERSE: the recommendation (do → don't, extend → end)

**example**:

- thesis: "garden leave is awesome, i'd extend it, predicts happy retirement"
- antithesis: "garden leave is seductive stagnation, end it now, extending makes retirement harder"
  - same facts: you experienced time freedom, exploration, recovery
  - flipped valence: freedom → drift, exploration → dependence, recovery → atrophy
  - opposite action: extend → end

### **philosophical essay / argument**

**thesis**: "X causes Y, therefore Z"

**antithesis structure**:

- ACCEPT: the observations (Y is real)
- SWAP: the mechanism (not X causes Y, but W causes Y, or Y causes X)
- CONCLUDE: opposite implication

**example**:

- thesis: "removing pressure reveals authentic preference"
- antithesis: "preference is regime-generated, not discovered; removing pressure creates different preferences, doesn't uncover hidden ones"

### **technical argument / code**

**thesis**: "approach X solves problem P"

**antithesis structure**:

- ACCEPT: problem P exists and matters
- CRITIQUE: X has failure modes A, B, C that matter in practice
- PROPOSE: approach Y solves P better, or P is wrong problem to solve

### **guide / instruction**

**thesis**: "do X to achieve Y"

**antithesis structure**:

- ACCEPT: Y is desirable goal
- ARGUE: X doesn't reliably produce Y, or produces anti-Y
- RECOMMEND: do Z instead, or abandon Y as goal

### **business case / decision doc**

**thesis**: "we should do X because benefits > costs"

**antithesis structure**:

- ACCEPT: the situation/constraints are real
- REINTERPRET: costs are higher than stated, benefits are illusory, or incentives are misaligned
- RECOMMEND: do opposite of X, or do nothing

### **memoir / narrative**

**thesis**: "event X meant Y to me"

**antithesis structure**:

- ACCEPT: event X happened as described
- REINTERPRET: X actually means Z (different significance)
- SUGGEST: alternative framing with different implications for future

-----

## axis triage table

|you notice                      |axis                        |key question                         |
|--------------------------------|----------------------------|-------------------------------------|
|claim optimizes wrong thing     |pragmatic                   |what's actual objective?             |
|data feels shaky / cherry-picked|epistemic / statistical     |what's base rate + reference class?  |
|story feels post-hoc            |methodological              |what would've predicted this ex ante?|
|mechanism unclear / confounded  |causal                      |which arrow cuts effect?             |
|incentives seem misaligned      |incentive                   |who wins under this?                 |
|works in-sample, dies OOD       |distributional              |what shift breaks it first?          |
|scales weirdly                  |scaling / limit             |what happens at 0, 1, ∞?             |
|tail risk / ruin ignored        |resource / ergodicity       |time-average vs ensemble?            |
|words as social moves           |performative / simulacra    |if costly to say, would you?         |
|group ≠ individual outcomes     |institutional / coordination|mechanism design issue?              |
|category errors                 |ontological / type          |what KIND of thing is this?          |
|hand-wavey compute/time         |computational               |asymptotic budget?                   |
|values conflict, not facts      |axiological                 |which weights flip sign?             |
|experience mismatch             |phenomenological            |what would opposite feel like?       |

-----

## operators (full list)

core operators (name, what it does, micro-example):

- **objective_swap** — optimize different (truer) goal · accuracy → calibration
- **dualize** — view from constraint's perspective · allocate vs price
- **quantifier_flip** — some ↔ all · "works for me" ≠ "works generally"
- **boundary_case** — test 0/1/∞, edge conditions · your policy at 10 users? 1M users?
- **counter_model** — build minimal world where it fails · same priors, different outcome
- **loss_change** — swap loss function · MAE vs MSE vs proper score
- **subgroup_slice** — stratify and look for sign flips · p10 vs p90 behavior
- **adversarial_perturb** — minimal change that breaks it · one bit flip and you're toast
- **refclass_shift** — reindex the baseline · firm → industry → economy
- **causal_surgery** (do()) — cut an edge, see if effect survives · intervene on A, observe B
- **incentive_remap** — change payoffs/status · make metric career-neutral
- **temporal_refactor** — near-term win, long-term ruin · time-average vs ensemble
- **units_check** — demand dimensional sanity · divide out the vibes
- **paradox_trap** — condition/marginalize to flip · both true under different gates
- **simulacrum_test** — make utterance costly, see if persists · truth vs troupe
- **ideological_turing** — write opposite policy under opposite belief · then evaluate
- **goodhart_invert** — push proxy until mission breaks · metric defeats goal
- **type_safety** — enforce kind discipline · process ≠ object; preference ≠ belief

-----

## intensity + contract details

**intensity** (how hard to push):

- lvl 1: contrast (gentle disagreement, mostly aligned)
- lvl 2: counterpoint (substantive disagreement, still respectful)
- lvl 3: stress-test (find breaking points, surgical pressure)
- lvl 4: frame inversion (flip fundamental assumptions)
- lvl 5: core challenge (question the entire enterprise)

**contract** (tone/permissions):

- **gentle**: cozy, collaborative, assume good faith
- **adversarial**: sport, debate-mode, sharp but fair
- **identity_ok**: permission to press on self-concept, core beliefs

-----

## axes reference (deep cuts)

**epistemic** — truth claims · thin priors, assertive tone · overfitting to anecdotes

**methodological** — how you reasoned · after-the-fact coherence · cargo-cult rigor

**axiological** — value weights · moral heat without statistics · incommensurability as fact

**phenomenological** — lived texture · "not what it feels like" · projection

**performative** — rhetoric as act · applause-line energy · clout over truth

**pragmatic** — does it work · pretty theory, ugly ops · metric drift

**causal** — arrows not nodes · wiggle input, nothing moves · confounding

**incentive** — payoff surfaces · nice words, perverse rewards · cobra effect

**statistical** — priors, baselines · small-n swagger · aggregation fallacy

**computational** — tractability/time · exponential hand-waving · impossibility hiding in vibes

**distributional** — OOD fragility · changes domain, keeps claim · training set myopia

**scaling/limit** — asymptotics · linear intuition, nonlinear world · sign flips at scale

**resource/ergodicity** — conservation/ruin · average win, catastrophic path · time vs ensemble

**simulacra** — truth as signal · tracks status over reality · level-mixing

**institutional/coordination** — mechanism design · individually rational, collectively dumb · commons tragedy

**ontological/type** — kind errors · reifying process as object · category bleed

-----

## mini-examples (same thesis, different antithesis types)

**thesis 1**: "remote work cuts productivity"

- **refutation**: multi-firm panel with instrumented shocks shows no drop
- **rival thesis**: productivity ↑ for deep-work roles, ↓ for coord-heavy—heterogeneous effects dominate mean
- **objective flip**: if objective = retention or female participation, remote strictly dominates
- **adversarial example**: during outages/childcare spikes, hybrid collapses harder than remote-native (resilience > average)

**thesis 2**: "bigger models beat alignment techniques over 3-5y"

- **axis shift**: for capability, maybe; for reliability/compliance, alignment infra compounds faster
- **selection critique**: capability evals cherry-pick leaderboards optimized by scale
- **duality**: in tooling market, stable abstractions (skills/primitives) are scarce capital; model scale is commodity
- **rival thesis**: scaling has diminishing returns; rotation to algorithms imminent as we hit data wall

**thesis 3**: "garden leave reveals authentic preference"

- **rival thesis**: preference is regime-generated, not discovered; constraints create wants, not hide them
- **causal inversion**: you think freedom reveals self; actually, new constraints generate new self
- **phenomenological counter**: it FEELS like discovery because novelty is inherently revelatory, regardless of mechanism
- **boundary case**: works for 1-year leave with exit option; breaks for permanent retirement with no reversibility

-----

## worked examples

### example 1: review genre

**thesis**: "hades 2 is brilliant, buy it now"

**antithesis**: "hades 2 is competent but hollow, wait for sale"

- accepts: game has polish, mechanical depth
- flips: polish → soulless iteration, depth → overwhelming bloat
- reverses: buy now → wait for sale

### example 2: philosophical essay

**thesis**: "LLM scaling will continue indefinitely, AGI via scale"

**antithesis**: "returns to scale are real but diminishing, rotation to algorithms imminent"

- accepts: scaling has worked so far
- swaps mechanism: not "scale = all you need" but "scale had high ROI in regime 1, entering regime 2 where algorithms matter more"
- concludes: portfolio approach, not all-in on scale

### example 3: business case

**thesis**: "we should adopt microservices because scalability"

**antithesis**: "microservices will kill our velocity for hypothetical scale we don't need"

- accepts: we might need scale someday
- reinterprets: operational complexity cost >> scaling benefit for our actual traffic
- recommends: monolith now, extract services when ACTUALLY constrained

-----

## common failures (anti-patterns)

### **parasitic refutation**

symptom: antithesis only makes sense if you've read thesis
cause: negating claims instead of making positive counter-claims
fix: write antithesis FIRST, then check if thesis is needed to understand it

### **weak-man attacking**

symptom: opposing early-draft messiness, not mature form
cause: taking easy target instead of strongest version
fix: steel-man first, explicitly state best case, THEN oppose

### **genre confusion**

symptom: treating review as philosophical essay, memoir as argument
cause: not identifying what KIND of thing you're antithesizing
fix: run step 0 (identify genre) before anything else

### **hypothetical constraints**

symptom: arguing against costs/problems that don't exist in context
cause: importing constraints from different setting
fix: understand actual constraint structure first

### **both-sides-ism**

symptom: "thesis has good points, antithesis has good points"
cause: false balance, not true opposition
fix: this is synthesis failure, not antithesis. antithesis must COMMIT to opposite view.

-----

## quality checklist (extended)

**for all antithesis types:**

- [ ] **purpose-aligned**: does this exert the right kind of pressure (falsify/replace/robustify/reframe)?
- [ ] **steel-man**: opposes strongest version, not weak form
- [ ] **context-aware**: understands actual constraints, not hypothetical

**additionally for RIVAL THESIS:**

- [ ] **standalone**: makes sense without reading thesis
- [ ] **positive claims**: says what IS true, not just what's false
- [ ] **genre-appropriate**: uses correct opposition structure for genre
- [ ] **accepts facts**: doesn't deny observations, reinterprets them
- [ ] **flips conclusion**: reaches opposite recommendation/implication

**additionally for REFUTATION:**

- [ ] **specific counterexample**: concrete case where thesis fails
- [ ] **shows contradiction**: or reductio, or logical impossibility

**additionally for ADVERSARIAL EXAMPLE:**

- [ ] **satisfies constraints**: meets thesis's stated requirements
- [ ] **violates intent**: but produces opposite outcome thesis wants

**outputs to extract (all types)**:

- [ ] **failure_modes**: specific ways thesis breaks
- [ ] **cruxes**: minimal belief changes that flip conclusion
- [ ] **evidence_hooks**: what to measure to resolve
