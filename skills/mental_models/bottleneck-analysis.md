# Bottleneck Analysis

The system is only as fast as its slowest component. Find the constraint before optimizing anything else.

## Process (Theory of Constraints)

1. **Identify** the constraint — where does work pile up? What has the longest queue?
2. **Exploit** the constraint — maximize throughput at the bottleneck with current resources
3. **Subordinate** everything else — non-bottleneck optimization is waste; align all other steps to feed the bottleneck efficiently
4. **Elevate** the constraint — invest to increase bottleneck capacity only after steps 2-3
5. **Repeat** — once elevated, a new bottleneck emerges. Go to step 1.

## Identification Signals

- Longest queue / most work-in-progress accumulation
- Most utilized resource (close to 100%)
- Step that, if doubled in capacity, would most increase system throughput
- Step that, if it goes down, stops everything

## Key Insight

Optimizing a non-bottleneck doesn't improve system throughput — it just builds up inventory before the bottleneck. Local optimization without global awareness creates waste.
