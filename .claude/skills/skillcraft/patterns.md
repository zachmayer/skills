# Advanced Workflow Patterns

Patterns from Anthropic's [Complete Guide to Building Skills](https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf) and [Best Practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices). These go beyond the basic patterns in SKILL.md.

## Contents
- Sequential workflow orchestration
- Multi-MCP coordination
- Iterative refinement
- Context-aware tool selection
- Domain-specific intelligence
- Research synthesis (no-code workflow)
- Style guide compliance (no-code feedback loop)

See also: [evaluation.md](evaluation.md), [code-skills.md](code-skills.md)

## Pattern 1: Sequential Workflow Orchestration

**Use when**: Users need multi-step processes in a specific order.

```markdown
# Workflow: Onboard New Customer

### Step 1: Create Account
Call MCP tool: `PayFlow:create_customer`
Parameters: name, email, company

### Step 2: Setup Payment
Call MCP tool: `PayFlow:setup_payment_method`
Wait for: payment method verification

### Step 3: Create Subscription
Call MCP tool: `PayFlow:create_subscription`
Parameters: plan_id, customer_id (from Step 1)

### Step 4: Send Welcome Email
Call MCP tool: `PayFlow:send_email`
Template: welcome_email_template
```

**Key techniques**:
- Explicit step ordering with dependencies between steps
- Validation at each stage
- Rollback instructions for failures
- Data passing between steps (customer_id from Step 1 used in Step 3)

## Pattern 2: Multi-MCP Coordination

**Use when**: Workflows span multiple services.

```markdown
# Design-to-Development Handoff

### Phase 1: Design Export (Figma MCP)
1. Export design assets from Figma
2. Generate design specifications
3. Create asset manifest

### Phase 2: Asset Storage (Drive MCP)
1. Create project folder in Drive
2. Upload all assets
3. Generate shareable links

### Phase 3: Task Creation (Linear MCP)
1. Create development tasks
2. Attach asset links to tasks
3. Assign to engineering team

### Phase 4: Notification (Slack MCP)
1. Post handoff summary to #engineering
2. Include asset links and task references
```

**Key techniques**:
- Clear phase separation
- Data passing between MCPs (asset links from Phase 2 used in Phase 3 and 4)
- Validation before moving to next phase
- Centralized error handling

## Pattern 3: Iterative Refinement

**Use when**: Output quality improves with iteration.

```markdown
# Iterative Report Creation

### Initial Draft
1. Fetch data via MCP
2. Generate first draft report
3. Save to temporary file

### Quality Check
1. Run validation script: `scripts/check_report.py`
2. Identify issues:
   - Missing sections
   - Inconsistent formatting
   - Data validation errors

### Refinement Loop
1. Address each identified issue
2. Regenerate affected sections
3. Re-validate
4. Repeat until quality threshold met

### Finalization
1. Apply final formatting
2. Generate summary
3. Save final version
```

**Key techniques**:
- Explicit quality criteria
- Validation scripts for objective checks
- Know when to stop iterating (define "good enough")

This extends the basic feedback loop pattern from SKILL.md with a full lifecycle.

## Pattern 4: Context-Aware Tool Selection

**Use when**: Same outcome, different tools depending on context.

```markdown
# Smart File Storage

### Decision Tree
1. Check file type and size
2. Determine best storage location:
   - Large files (>10MB): Use cloud storage MCP
   - Collaborative docs: Use Notion/Docs MCP
   - Code files: Use GitHub MCP
   - Temporary files: Use local storage

### Execute Storage
Based on decision:
- Call appropriate MCP tool
- Apply service-specific metadata
- Generate access link

### Provide Context to User
Explain why that storage was chosen
```

**Key techniques**:
- Clear decision criteria
- Fallback options
- Transparency about choices (tell the user why)

## Pattern 5: Domain-Specific Intelligence

**Use when**: Your skill adds specialized knowledge beyond tool access.

```markdown
# Payment Processing with Compliance

### Before Processing (Compliance Check)
1. Fetch transaction details via MCP
2. Apply compliance rules:
   - Check sanctions lists
   - Verify jurisdiction allowances
   - Assess risk level
3. Document compliance decision

### Processing
IF compliance passed:
- Call payment processing MCP tool
- Apply appropriate fraud checks
- Process transaction
ELSE:
- Flag for review
- Create compliance case

### Audit Trail
- Log all compliance checks
- Record processing decisions
- Generate audit report
```

**Key techniques**:
- Domain expertise embedded in logic (compliance rules)
- Compliance before action (gate pattern)
- Comprehensive documentation and audit trail

## Pattern 6: Research Synthesis (No-Code Workflow)

**Use when**: Complex analysis tasks that don't require scripts. From the [Best Practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) guide.

````markdown
## Research Synthesis Workflow

Copy this checklist and track your progress:

```
Research Progress:
- [ ] Step 1: Read all source documents
- [ ] Step 2: Identify key themes
- [ ] Step 3: Cross-reference claims
- [ ] Step 4: Create structured summary
- [ ] Step 5: Verify citations
```

**Step 1: Read all source documents**
Review each document in the `sources/` directory. Note main arguments and supporting evidence.

**Step 2: Identify key themes**
Look for patterns across sources. What themes appear repeatedly? Where do sources agree or disagree?

**Step 3: Cross-reference claims**
For each major claim, verify it appears in source material. Note which source supports each point.

**Step 4: Create structured summary**
Organize findings by theme. Include:
- Main claim
- Supporting evidence from sources
- Conflicting viewpoints (if any)

**Step 5: Verify citations**
Check that every claim references the correct source. If incomplete, return to Step 3.
````

This demonstrates that the workflow and checklist patterns work for analysis tasks, not just code tasks.

## Style Guide Compliance (No-Code Feedback Loop)

A validation loop using reference documents instead of scripts:

```markdown
## Content Review Process

1. Draft content following guidelines in STYLE_GUIDE.md
2. Review against checklist:
   - Check terminology consistency
   - Verify examples follow the standard format
   - Confirm all required sections are present
3. If issues found:
   - Note each issue with specific section reference
   - Revise the content
   - Review checklist again
4. Only proceed when all requirements are met
5. Finalize and save
```

The "validator" is STYLE_GUIDE.md, and Claude performs the check by reading and comparing.
