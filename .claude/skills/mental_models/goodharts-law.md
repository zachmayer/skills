# Goodhart's Law

When a measure becomes a target, it ceases to be a good measure. People optimize the metric, not the underlying goal.

## Mechanism

Metrics are proxies for things we actually care about. When you incentivize the proxy, people find ways to improve the proxy without improving the underlying thing. The metric gets "gamed" — it goes up while the thing it measured goes down.

## Examples

- Lines of code as productivity metric → verbose, duplicated code
- Test coverage as quality metric → tests that exercise code without asserting anything useful
- Response time targets → gaming the measurement, not improving the system
- Revenue targets without profit → sell at a loss, hit the number

## Counters

- **Counter-metrics:** measure what you refuse to sacrifice alongside what you optimize
- **Rotate metrics:** change what you measure periodically so gaming strategies can't ossify
- **Qualitative review:** supplement metrics with human judgment
- **Measure outcomes, not outputs:** measure customer satisfaction, not tickets closed
