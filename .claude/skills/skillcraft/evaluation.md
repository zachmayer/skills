# Evaluation and Iterative Development

How to evaluate skill effectiveness and improve skills through iteration.

## Contents
- Success criteria
- Testing approach
- Evaluation-driven development
- Evaluation structure
- Iterative development with Claude
- Iteration based on feedback
- Observing skill behavior
- Team feedback

## Success Criteria

How will you know your skill is working? These are aspirational targets — rough benchmarks rather than precise thresholds.

### Quantitative metrics

- **Skill triggers on 90% of relevant queries** — *How to measure*: Run 10-20 test queries that should trigger your skill. Track how many times it loads automatically vs. requires explicit invocation
- **Completes workflow in X tool calls** — *How to measure*: Compare the same task with and without the skill enabled. Count tool calls and total tokens consumed
- **0 failed API calls per workflow** — *How to measure*: Monitor MCP server logs during test runs. Track retry rates and error codes

### Qualitative metrics

- **Users don't need to prompt Claude about next steps** — *How to assess*: During testing, note how often you need to redirect or clarify. Ask beta users for feedback
- **Workflows complete without user correction** — *How to assess*: Run the same request 3-5 times. Compare outputs for structural consistency and quality
- **Consistent results across sessions** — *How to assess*: Can a new user accomplish the task on first try with minimal guidance?

## Testing Approach

Effective skills testing covers three areas:

### 1. Triggering tests

Goal: Ensure your skill loads at the right times.

```
Should trigger:
- "Help me set up a new ProjectHub workspace"
- "I need to create a project in ProjectHub"
- "Initialize a ProjectHub project for Q4 planning"

Should NOT trigger:
- "What's the weather in San Francisco?"
- "Help me write Python code"
- "Create a spreadsheet" (unless your skill handles sheets)
```

### 2. Functional tests

Goal: Verify the skill produces correct outputs.

Test cases: valid outputs generated, API calls succeed, error handling works, edge cases covered.

### 3. Performance comparison

Goal: Prove the skill improves results vs. baseline.

```
Without skill:
- User provides instructions each time
- 15 back-and-forth messages
- 3 failed API calls requiring retry
- 12,000 tokens consumed

With skill:
- Automatic workflow execution
- 2 clarifying questions only
- 0 failed API calls
- 6,000 tokens consumed
```

**Pro tip**: Iterate on a single task before expanding. The most effective skill creators iterate on a single challenging task until Claude succeeds, then extract the winning approach into a skill. This leverages Claude's in-context learning and provides faster signal than broad testing.

## Evaluation-Driven Development

Build evaluations BEFORE writing docs. This ensures your skill solves real problems.

1. **Identify gaps**: Run Claude on representative tasks without a skill. Document specific failures
2. **Create evaluations**: Build 3+ scenarios that test these gaps
3. **Establish baseline**: Measure Claude's performance without the skill
4. **Write minimal instructions**: Just enough to address gaps and pass evaluations
5. **Iterate**: Run evals, compare against baseline, refine

## Evaluation Structure

```json
{
  "skills": ["pdf-processing"],
  "query": "Extract all text from this PDF file and save it to output.txt",
  "files": ["test-files/document.pdf"],
  "expected_behavior": [
    "Reads PDF using appropriate library or tool",
    "Extracts text from all pages without missing any",
    "Saves extracted text to output.txt in readable format"
  ]
}
```

There is no built-in evaluation runner. Create your own system using this structure as a guide.

## Iterative Development with Claude

Work with two instances:
- **Claude A**: Helps design and refine the skill (the author)
- **Claude B**: Tests the skill on real tasks (the user)

### Creating a New Skill

1. **Complete a task without a skill**: Work through a problem with Claude A. Notice what context you repeatedly provide
2. **Identify the reusable pattern**: What knowledge would help with similar future tasks?
3. **Ask Claude A to create the skill**: Claude understands the SKILL.md format natively
4. **Review for conciseness**: "Remove the explanation about what X means — Claude already knows that"
5. **Improve information architecture**: "Organize so the schema is in a separate reference file"
6. **Test with Claude B**: Use the skill on related tasks with a fresh instance
7. **Iterate**: If Claude B struggles, bring specifics back to Claude A

### Improving Existing Skills

1. **Use the skill in real workflows** with Claude B on actual tasks
2. **Observe behavior**: Note struggles, successes, unexpected choices
3. **Return to Claude A**: "Claude B forgot to filter test accounts. The rule isn't prominent enough?"
4. **Apply changes**: Claude A suggests restructuring, stronger language, etc.
5. **Test again**: Verify improvements with Claude B
6. **Repeat**: Each iteration improves based on real behavior, not assumptions

## Iteration Based on Feedback

Skills are living documents. Plan to iterate based on:

### Undertriggering signals
- Skill doesn't load when it should
- Users manually enabling it
- Support questions about when to use it

**Solution**: Add more detail and nuance to the description — include keywords, particularly for technical terms.

### Overtriggering signals
- Skill loads for irrelevant queries
- Users disabling it
- Confusion about purpose

**Solution**: Add negative triggers (`Do NOT use for...`), be more specific about scope.

### Execution issues
- Inconsistent results
- API call failures
- User corrections needed

**Solution**: Improve instructions, add error handling, use scripts for critical validation.

## Observing Skill Behavior

Watch for these patterns in how Claude uses skills:

- **Unexpected exploration paths**: Claude reads files in an unanticipated order → structure may not be intuitive
- **Missed connections**: Claude fails to follow references → links need to be more explicit
- **Overreliance on certain sections**: Claude repeatedly reads the same file → consider moving that content to main SKILL.md
- **Ignored content**: Claude never accesses a bundled file → it may be unnecessary or poorly signaled

The `name` and `description` fields are particularly critical — they determine whether Claude triggers the skill at all.

## Stolen Skill Evaluation

When evaluating a skill created via [skill-stealer.md](skill-stealer.md), focus on completeness — the biggest risk is losing key ideas during extraction.

### Checklist

1. **Enumerate source ideas** — List every major idea, procedure, and distinction from the original source. This is your completeness baseline.
2. **Map to stolen skill** — For each source idea, confirm it appears in the stolen skill (possibly reworded or converted from code to prose). Flag anything missing.
3. **Justify cuts** — Any source idea NOT in the stolen skill needs an explicit reason: "Claude already knows this", "framework-specific boilerplate", or "not applicable to our architecture". If you can't justify the cut, restore the idea.
4. **Trigger coverage** — 5+ positive queries, 5+ negative queries. Does the `description` field surface the skill for the right requests?
5. **Functional scenarios** — 3+ realistic use cases. Walk through the skill mentally: would it produce correct output?
6. **Freedom levels** — Are the right parts locked down (low freedom) vs. flexible (high freedom)?

### Common Failure Modes

- **Over-compression**: "Minimum effective prompt" strips procedural distinctions that the model won't reinvent (e.g., b1 vs b2 classification, specific scoring formulas, taxonomies)
- **Lost code logic**: Converting scripts to prose is fine, but the prose must capture the same decision logic — not just "handle errors appropriately"
- **Trigger blindness**: The stolen skill works but never activates because the description lacks the keywords users actually type

## Team Feedback

1. Share skills with teammates and observe usage
2. Ask: Does the skill activate when expected? Are instructions clear? What's missing?
3. Incorporate feedback to address blind spots in your own usage patterns
