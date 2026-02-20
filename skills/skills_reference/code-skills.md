# Skills with Executable Code

Detailed guidance for skills that include scripts and executable code.

## Contents
- Fail clearly, don't swallow
- Configuration constants
- Utility scripts
- Visual analysis
- Verifiable intermediate outputs
- Dependencies and runtime
- MCP tool references

## Fail Clearly, Don't Swallow

Scripts should fail with clear, actionable error messages — not silently recover. The agent is intelligent; let it reason about errors in context rather than pre-specifying all error handling.

> **Note**: Anthropic's best practices recommend scripts handle errors rather than punt to Claude. We take a more targeted position: validate inputs up front (preconditions), but let runtime errors bubble up with clear messages. The agent reasons about unexpected failures better than pre-written catch-all handlers.

```python
# Good: fail with a clear message the agent can act on
def process_file(path):
    if not os.path.exists(path):
        raise click.ClickException(f"File not found: {path}")
    with open(path) as f:
        return f.read()

# Bad: silently swallow errors
def process_file(path):
    try:
        with open(path) as f:
            return f.read()
    except FileNotFoundError:
        return ""  # Agent never knows the file was missing
```

**Validate inputs, don't catch outcomes.** Check preconditions up front (file exists, required fields present, API key set). Use type hints, type checking, and runtime type validation as your first line of defense — Pydantic is ideal for this: declare the shape of valid input and let validation errors speak for themselves. Let runtime errors bubble up with their natural error messages — the agent can diagnose and recover better than pre-written exception handlers.

## Configuration Constants

Document why constants have specific values. No "voodoo constants."

```python
# Good: self-documenting
REQUEST_TIMEOUT = 30  # HTTP requests typically complete within 30s
MAX_RETRIES = 3       # Most intermittent failures resolve by 2nd retry

# Bad: magic numbers
TIMEOUT = 47  # Why 47?
RETRIES = 5   # Why 5?
```

## Utility Scripts

Pre-made scripts beat generated code: more reliable, save tokens and time, ensure consistency.

Make clear whether Claude should **execute** or **read** a script:
- "Run `analyze_form.py` to extract fields" (execute — most common)
- "See `analyze_form.py` for the extraction algorithm" (read as reference)

Document each script's interface:

````markdown
**analyze_form.py**: Extract form fields from PDF
```bash
python scripts/analyze_form.py input.pdf > fields.json
```
Output format:
```json
{"field_name": {"type": "text", "x": 100, "y": 200}}
```

**validate.py**: Check for errors
```bash
python scripts/validate.py fields.json
# Returns: "OK" or lists conflicts
```
````

## Visual Analysis

When inputs can be rendered as images, have Claude analyze them visually. Claude's vision capabilities help understand layouts and structures.

```markdown
1. Convert PDF to images: `python scripts/pdf_to_images.py form.pdf`
2. Analyze each page image to identify form fields
```

## Verifiable Intermediate Outputs

The "plan-validate-execute" pattern catches errors early:

1. Analyze inputs
2. **Create plan file** (e.g., `changes.json`)
3. **Validate plan** with a script
4. Execute changes
5. Verify output

Why this works:
- Catches errors before changes are applied
- Machine-verifiable with objective validation
- Reversible planning (iterate on plan without touching originals)
- Clear debugging with specific error messages

When to use: batch operations, destructive changes, complex validation rules, high-stakes operations.

Make validation scripts verbose:
```
Error: Field 'signature_date' not found.
Available fields: customer_name, order_total, signature_date_signed
```

## Dependencies and Runtime

### Claude Code
- Full network access, same as any program on the user's computer
- Avoid global package installs; install locally to avoid interfering with user's system
- Prefer modern package managers: `uv` for Python, `pnpm`/`bun` for TypeScript/JS. Use inline script dependencies (`uv run --with`) or project-level deps over global installs

### Claude API
- No network access, no runtime package installation
- Only pre-installed packages available
- Check code execution tool docs for available packages

### Claude.ai
- Varying network access depending on user/admin settings
- Can install packages from npm and PyPI

Always list required packages in SKILL.md and verify availability.

## MCP Tool References

Always use fully qualified tool names: `ServerName:tool_name`

```markdown
Use the BigQuery:bigquery_schema tool to retrieve table schemas.
Use the GitHub:create_issue tool to create issues.
```

Without the server prefix, Claude may fail to locate the tool when multiple MCP servers are available.
