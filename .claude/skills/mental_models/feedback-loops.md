# Feedback Loops

Identify reinforcing loops (growth/collapse spirals) and balancing loops (stability). Most bugs in complex systems are feedback loops you didn't see.

## Types

**Reinforcing (positive) loops** — output amplifies input. Growth spirals (viral adoption, compound interest) and collapse spirals (bank runs, death spirals). Look for: "more X leads to more Y, which leads to more X."

**Balancing (negative) loops** — output dampens input. Thermostats, market corrections, homeostasis. Look for: "more X leads to less Y, which reduces X."

## Process

1. **Map the system** — identify key variables and how they influence each other
2. **Trace the loops** — follow chains of causation back to their starting variable
3. **Classify** — reinforcing or balancing? What's the sign of the loop?
4. **Find delays** — feedback loops with delays oscillate and overshoot
5. **Identify dominant loop** — which loop currently dominates system behavior?

## Key Patterns

- **Delays cause oscillation** — thermostat with delay overshoots both ways
- **Reinforcing loops need governors** — unchecked, they either explode or collapse
- **Competing loops** — systems often have reinforcing AND balancing loops; behavior depends on which dominates at current state
- **Hidden reinforcing loops** — the most dangerous ones are those you don't see until they're dominating
