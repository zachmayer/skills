# Post-Mortem

After a failure, structured diagnosis before taking corrective action. The complement to pre-mortem — pre-mortem prevents failures, post-mortem learns from them.

## Process

1. **State what happened** — exact error, test name, observable symptom. No interpretation yet.
2. **State what you expected** — what should have happened instead?
3. **Trace root cause** — follow the data, don't guess. Use Five Whys if needed. The first explanation is usually a symptom, not the cause.
4. **Classify the failure** — what type of failure is this?
   - **Wrong assumption**: your mental model of the code/system was incorrect
   - **Wrong approach**: the strategy itself is flawed, not just the execution
   - **Scope error**: solved the wrong problem or missed a constraint
   - **Flaky/environmental**: non-deterministic failure, not a logic error
5. **Plan the fix** — specific change to make, based on root cause (not the symptom)
6. **Define validation** — how will you confirm the fix worked and didn't introduce regressions?

## Decision After Diagnosis

| Classification | Action |
|---------------|--------|
| Wrong assumption | Fix the assumption, retry same approach |
| Wrong approach | Pivot to a fundamentally different strategy |
| Scope error | Step back, redefine the problem, then re-plan |
| Flaky/environmental | Retry once, add resilience if it recurs |

## When to Use

- After any failed attempt before retrying — prevents blind retry loops
- After a test failure in a development loop
- After a deployment failure
- When debugging: after each hypothesis is disproven

## Key Principle

Agents that diagnose failures before acting recover faster than agents that immediately retry. Inspired by the Darwin Godel Machine's `diagnose_problem()` pattern — separate diagnosis (understanding) from repair (action).
