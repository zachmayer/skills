---
name: skillcraft
description: >
  Unified skill for authoring, extracting, and maintaining Agent Skills.
  Covers creating new skills, reviewing skill quality, best practices for
  SKILL.md authoring, the Agent Skills standard, progressive disclosure,
  and evaluation. Use when the user says "creating new skills", "review my
  skills", "audit skills", "clean up skills", "too many skills", "steal
  this skill", "convert this to a skill", "make a skill from this", shares
  a link to a prompt or workflow, or needs best practices for SKILL.md.
  Do NOT use for general Claude Code configuration (use config reference).
---

# Skillcraft

Unified entry point for building, extracting, and maintaining Agent Skills.

## Quick Lookup

| Need | Read |
|:-----|:-----|
| Author a new skill, frontmatter, structure, patterns | [skills-reference.md](skills-reference.md) |
| Extract a skill from a URL or workflow | [skill-stealer.md](skill-stealer.md) |
| Audit / compress / clean up existing skills | [skill-pruner.md](skill-pruner.md) |

## Sub-Skills

### Skills Reference
Comprehensive reference for writing effective SKILL.md files: structure, frontmatter, naming, descriptions, progressive disclosure, patterns, anti-patterns, and evaluation. Has its own reference files for deep dives:
- [code-skills.md](code-skills.md), [patterns.md](patterns.md), [mcp-integration.md](mcp-integration.md)
- [evaluation.md](evaluation.md), [troubleshooting.md](troubleshooting.md), [distribution.md](distribution.md), [resources.md](resources.md)

See [skills-reference.md](skills-reference.md).

### Skill Stealer
Extracts a reusable agent skill from a URL (GitHub repo, blog post, tweet, or any source describing an AI workflow or prompt). Distills the core idea into a clean SKILL.md following the Agent Skills standard. Can also steal code, rewriting scripts to Python with Click CLIs run via uv.

See [skill-stealer.md](skill-stealer.md).

### Skill Pruner
Audits all installed skills for quality, redundancy, and overlap against the Agent Skills standard. Surfaces candidates for merging, trimming, compression, or deletion. Includes the empirically validated Skill Compression methodology.

See [skill-pruner.md](skill-pruner.md).

## Typical Workflows

1. **Build a new skill from scratch**: Read [skills-reference.md](skills-reference.md), then author SKILL.md
2. **Steal a skill from a URL**: Run [skill-stealer.md](skill-stealer.md), then compress with [skill-pruner.md](skill-pruner.md) if >150 lines
3. **Periodic maintenance**: Run [skill-pruner.md](skill-pruner.md) to audit all skills
