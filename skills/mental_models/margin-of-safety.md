# Margin of Safety

Build in buffer for the unknown. The margin between your estimate and failure is your insurance against being wrong.

## Application

- **Estimates:** if you think something takes 3 days, plan for 5. Your estimate is almost certainly optimistic.
- **Architecture:** design for 10x current load, not 1.5x. The difference in cost is small; the difference in resilience is large.
- **Dependencies:** don't depend on things working perfectly. What's your plan when the third-party API is down?
- **Deadlines:** buffer between internal deadline and external commitment

## Key Insight

The margin of safety isn't waste — it's the price of operating in an uncertain world. The question isn't "will I need this buffer?" but "can I afford NOT having it when I'm wrong?"
