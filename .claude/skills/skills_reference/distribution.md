# Distribution and Sharing

How to distribute and share skills. From Anthropic's [Complete Guide to Building Skills](https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf).

## Contents
- Installation methods
- Organization deployment
- Skills via API
- The open standard
- GitHub hosting
- Positioning your skill

## Installation Methods

### Individual users
1. Download the skill folder
2. Zip the folder (if needed)
3. Upload to Claude.ai via Settings > Capabilities > Skills
4. Or place in Claude Code skills directory (`~/.claude/skills/<name>/` for personal, `.claude/skills/<name>/` for project)

### Organization-level
- Admins can deploy skills workspace-wide via managed settings
- Automatic updates
- Centralized management

## Skills via API

For programmatic use cases — building applications, agents, or automated workflows:

- `/v1/skills` endpoint for listing and managing skills
- Add skills to Messages API requests via the `container.skills` parameter
- Version control and management through the Claude Console
- Works with the Claude Agent SDK for building custom agents

| Use Case | Best Surface |
|:---|:---|
| End users interacting directly | Claude.ai / Claude Code |
| Manual testing during development | Claude.ai / Claude Code |
| Individual, ad-hoc workflows | Claude.ai / Claude Code |
| Applications using skills programmatically | API |
| Production deployments at scale | API |
| Automated pipelines and agent systems | API |

Skills in the API require the Code Execution Tool beta.

See: [Skills API Quickstart](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/quickstart), [Create Custom Skills](https://platform.claude.com/docs/en/api/skills/create-skill), [Skills in the Agent SDK](https://platform.claude.com/docs/en/agent-sdk/skills)

## The Open Standard

Skills are published as an [open standard (agentskills.io)](https://agentskills.io). Like MCP, skills are designed to be portable across tools and platforms — the same skill should work whether you're using Claude or other AI platforms. Authors can note platform-specific requirements in the `compatibility` field.

## GitHub Hosting

Recommended approach for sharing skills:

### 1. Host on GitHub
- Public repo for open-source skills
- Clear README with installation instructions (repo-level, NOT inside the skill folder)
- Example usage and screenshots

### 2. Document in Your MCP Repo (if applicable)
- Link to skills from MCP documentation
- Explain the value of using both together
- Provide quick-start guide

### 3. Create an Installation Guide

```markdown
# Installing the [Your Service] skill

1. **Download the skill**:
   - Clone repo: `git clone https://github.com/yourcompany/skills`
   - Or download ZIP from Releases

2. **Install in Claude**:
   - Open Claude.ai > Settings > Skills
   - Click "Upload skill"
   - Select the skill folder (zipped)

3. **Enable the skill**:
   - Toggle on the [Your Service] skill
   - Ensure your MCP server is connected (if applicable)

4. **Test**:
   - Ask Claude: "Set up a new project in [Your Service]"
```

## Positioning Your Skill

How you describe your skill determines whether users understand its value.

### Focus on outcomes, not features

```markdown
# Good — user benefit
"The ProjectHub skill enables teams to set up complete project
workspaces in seconds — including pages, databases, and templates —
instead of spending 30 minutes on manual setup."

# Bad — implementation details
"The ProjectHub skill is a folder containing YAML frontmatter and
Markdown instructions that calls our MCP server tools."
```

### Highlight the MCP + Skills story (if applicable)

```markdown
"Our MCP server gives Claude access to your Linear projects.
Our skills teach Claude your team's sprint planning workflow.
Together, they enable AI-powered project management."
```

Skills make your MCP integration more complete. As users compare connectors, those with skills offer a faster path to value.
