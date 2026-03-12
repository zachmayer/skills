# Skills + MCP Integration

How skills enhance MCP (Model Context Protocol) integrations. From Anthropic's [Complete Guide to Building Skills](https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf).

## Contents
- The kitchen analogy
- Why MCP users need skills
- MCP vs skills responsibilities
- Building skills for your MCP server
- Common MCP patterns

## The Kitchen Analogy

MCP provides the professional kitchen: access to tools, ingredients, and equipment. Skills provide the recipes: step-by-step instructions on how to create something valuable. Together, they enable users to accomplish complex tasks without needing to figure out every step themselves.

## MCP vs Skills: Responsibilities

| MCP (Connectivity) | Skills (Knowledge) |
|:---|:---|
| Connects Claude to your service (Notion, Asana, Linear, etc.) | Teaches Claude how to use your service effectively |
| Provides real-time data access and tool invocation | Captures workflows and best practices |
| What Claude **can** do | How Claude **should** do it |

## Why MCP Users Need Skills

**Without skills**:
- Users connect your MCP but don't know what to do next
- Support tickets asking "how do I do X with your integration"
- Each conversation starts from scratch
- Inconsistent results because users prompt differently each time
- Users blame your connector when the real issue is workflow guidance

**With skills**:
- Pre-built workflows activate automatically when needed
- Consistent, reliable tool usage
- Best practices embedded in every interaction
- Lower learning curve for your integration

## Building Skills for Your MCP Server

If you already have a [working MCP server](https://support.claude.com/en/articles/10949351-getting-started-with-local-mcp-servers-on-claude-desktop), you've done the hard part. Skills are the knowledge layer on top — capturing the workflows and best practices you already know.

### Two paths

- **Building standalone skills (no MCP)?** Focus on the main SKILL.md reference — Fundamentals, Planning and Design, use case categories 1-2.
- **Enhancing an MCP integration?** This file and use case category 3 (MCP Enhancement) are for you.

Both paths share the same technical requirements (SKILL.md structure, frontmatter, progressive disclosure).

### MCP Tool References

Always use fully qualified tool names to avoid "tool not found" errors: `ServerName:tool_name`

```markdown
# Good — fully qualified
Use the BigQuery:bigquery_schema tool to retrieve table schemas.
Use the GitHub:create_issue tool to create issues.

# Bad — ambiguous when multiple MCP servers are available
Use the bigquery_schema tool to retrieve table schemas.
```

### MCP Connection Troubleshooting

If your skill loads but MCP tool calls fail:

1. **Verify MCP server is connected**: Claude.ai: Settings > Extensions > [Your Service]. Should show "Connected"
2. **Check authentication**: API keys valid and not expired, proper permissions/scopes granted, OAuth tokens refreshed
3. **Test MCP independently**: Ask Claude to call MCP directly without the skill — "Use [Service] MCP to fetch my projects". If this fails, the issue is MCP configuration, not the skill
4. **Verify tool names**: Skill must reference correct MCP tool names (case-sensitive). Use fully qualified `ServerName:tool_name` format. Check your MCP server documentation

## Common MCP Skill Patterns

### Sequential MCP Orchestration
Multi-step processes using a single MCP server in order. See [patterns.md](patterns.md) Pattern 1.

### Multi-MCP Coordination
Workflows that span multiple services (e.g., Figma + Drive + Linear + Slack). See [patterns.md](patterns.md) Pattern 2.

### MCP Enhancement (Category 3)
Adding workflow guidance on top of raw tool access. The [sentry-code-review skill](https://github.com/getsentry/sentry-for-claude/tree/main/skills) is a real example — it coordinates multiple Sentry MCP calls in sequence, embeds domain expertise, and provides context users would otherwise need to specify.

Key techniques:
- Coordinate multiple MCP calls in sequence
- Embed domain expertise (e.g., compliance rules, best practices)
- Provide context users would otherwise need to specify
- Include error handling for common MCP issues

### Positioning Your MCP + Skills Story

When documenting or marketing your integration:

```markdown
# Good — focus on outcomes
"Our MCP server gives Claude access to your Linear projects.
Our skills teach Claude your team's sprint planning workflow.
Together, they enable AI-powered project management."

# Bad — focus on implementation details
"The skill is a folder containing YAML frontmatter and Markdown
instructions that calls our MCP server tools."
```
