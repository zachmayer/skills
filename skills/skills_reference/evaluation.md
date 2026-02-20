# Evaluation and Iterative Development

How to evaluate skill effectiveness and improve skills through iteration.

## Contents
- Evaluation-driven development
- Evaluation structure
- Iterative development with Claude
- Observing skill behavior
- Team feedback

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

## Observing Skill Behavior

Watch for these patterns in how Claude uses skills:

- **Unexpected exploration paths**: Claude reads files in an unanticipated order → structure may not be intuitive
- **Missed connections**: Claude fails to follow references → links need to be more explicit
- **Overreliance on certain sections**: Claude repeatedly reads the same file → consider moving that content to main SKILL.md
- **Ignored content**: Claude never accesses a bundled file → it may be unnecessary or poorly signaled

The `name` and `description` fields are particularly critical — they determine whether Claude triggers the skill at all.

## Team Feedback

1. Share skills with teammates and observe usage
2. Ask: Does the skill activate when expected? Are instructions clear? What's missing?
3. Incorporate feedback to address blind spots in your own usage patterns
