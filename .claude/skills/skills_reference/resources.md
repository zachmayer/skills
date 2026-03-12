# Resources and References

Official documentation, blog posts, and example skills for building Agent Skills.

## Contents
- Official documentation
- Blog posts
- Example skills
- Tools and utilities

## Official Documentation

- [Best Practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) — web docs on skill authoring
- [Skills Overview](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview) — how skills work, architecture
- [Skills Quickstart](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/quickstart) — create your first skill
- [Skills API](https://platform.claude.com/docs/en/api/overview) — programmatic skill management
- [Agent SDK Skills](https://platform.claude.com/docs/en/agent-sdk/skills) — skills in TypeScript/Python SDK
- [Agent Skills Standard](https://agentskills.io) — the open standard
- [Complete Guide PDF](https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf) — comprehensive PDF guide
- [MCP Documentation](https://modelcontextprotocol.io) — Model Context Protocol

## Blog Posts

- [Introducing Agent Skills](https://claude.com/blog/skills)
- [Engineering: Equipping Agents for the Real World](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)
- [Skills Explained](https://www.claude.com/blog/skills-explained)
- [How to Create Skills](https://www.claude.com/blog/how-to-create-skills-key-steps-limitations-and-examples)
- [Building Skills for Claude Code](https://www.claude.com/blog/building-skills-for-claude-code)
- [Improving Frontend Design through Skills](https://www.claude.com/blog/improving-frontend-design-through-skills)

## Example Skills

- [anthropics/skills](https://github.com/anthropics/skills) — Anthropic-created skills you can customize
  - [frontend-design](https://github.com/anthropics/skills/tree/main/skills/frontend-design) — production-grade frontend interfaces
  - [skill-creator](https://github.com/anthropics/skills/blob/main/skills/skill-creator/SKILL.md) — interactive skill authoring guide
  - [pdf](https://github.com/anthropics/skills/tree/main/skills/pdf), [docx](https://github.com/anthropics/skills/tree/main/skills/docx), [pptx](https://github.com/anthropics/skills/tree/main/skills/pptx), [xlsx](https://github.com/anthropics/skills/tree/main/skills/xlsx) — document creation
- [Partner Skills Directory](https://www.claude.com/connectors) — skills from Asana, Atlassian, Canva, Figma, Sentry, Zapier, and more
- [sentry-code-review](https://github.com/getsentry/sentry-for-claude/tree/main/skills) — MCP enhancement example from Sentry

## Tools and Utilities

**skill-creator skill**: Available in the [anthropics/skills](https://github.com/anthropics/skills) repository. Generates skills from descriptions, reviews skills for common issues, suggests test cases. Use: "Help me build a skill using skill-creator". Note: helps design and refine skills but does not run automated test suites.

## Important: Local vs External Resources

When authoring skills, distinguish between:

- **Local reference files**: Bundled in the skill directory, loadable via progressive disclosure. Use for critical guidance that Claude must have access to
- **External links**: Only fetchable if network access is available. Use for citations and supplementary material, not runtime-critical context

If information is essential for the skill to work correctly, bundle it locally — don't rely on external URLs being accessible.
