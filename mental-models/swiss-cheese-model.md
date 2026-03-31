# Swiss Cheese Model

Every defense has holes. Disasters happen when the holes align.

James Reason's model from aviation safety: each layer of defense (procedure, tool, review, training) is like a slice of Swiss cheese — imperfect, with holes that shift over time. A single hole rarely causes failure. Failure occurs when holes in multiple layers line up, allowing a hazard to pass through every defense undetected.

## Application

- **In analysis:** Your methodology has multiple layers (EDA, rules, ML, review). Each has blind spots. Safety comes from ensuring the blind spots don't overlap — not from any single layer being perfect.
- **In engineering:** Code review catches what tests miss. Tests catch what the type system misses. The type system catches what the developer misses. No layer is sufficient alone.
- **In decision-making:** First-principles reasoning, data analysis, expert opinion, and red-teaming are all imperfect. Use multiple and check where their holes overlap.

## Process

1. **List your defense layers.** What methods, tools, checks, and reviews are in place?
2. **Identify the holes in each layer.** What can each method NOT detect? What assumptions does each make?
3. **Check for alignment.** Is there a failure mode that passes through every layer? If so, you have an aligned-holes problem.
4. **Add or rotate layers.** Either add a new defense that covers the aligned hole, or modify an existing layer to close it.

## Key Insight

The instinct when you find a hole is to document it. The correct response is to add another slice of cheese. Documentation tells people the hole exists. Another layer prevents hazards from passing through.

This directly connects to **Countermeasure, Not Caveat**: finding a hole is the observation; adding a layer is the countermeasure; documenting the hole without adding a layer is the caveat trap.

## When to Use

- When designing a methodology with multiple detection or validation steps
- When reviewing a system for robustness (not just correctness)
- When a known failure mode exists and you need to decide: add a layer, or accept the risk?
- After a failure: which layers had aligned holes?

## Source

James Reason, *Human Error* (1990) and *Managing the Risks of Organizational Accidents* (1997). Originally developed for aviation and nuclear safety; widely applied in healthcare, engineering, and organizational risk management.
