# /// script
# dependencies = ["anthropic>=0.40", "click>=8.0"]
# ///
"""RLM — Recursive Language Model analysis for large files.

Ported from https://github.com/mahanswaray/rlm-ts-aisdk (TypeScript/Vercel AI SDK)
to Python/Click/Anthropic SDK. Root LLM iteratively writes Python code in a
persistent REPL, delegating chunk analysis to cheap sub-LLMs via llmQuery().
"""

import io
import json
import os
import re
import sys
from contextlib import redirect_stdout
from typing import Optional

import anthropic
import click

SYSTEM_PROMPT = """\
You analyze large files using a 3-phase Recursive Language Model (RLM) strategy.

Pre-injected environment (no imports needed):
- contextPath: str — absolute path to the context file
- llmQuery(prompt: str) -> str — ask sub-LLM a focused question, returns answer
- open, re, json, os — standard builtins

Write Python code in ```python blocks. Variables persist between iterations.

Strategy:
1. Recon: read the file, check size, identify format and natural chunk boundaries
2. Filter+Analyze: split by structure, call llmQuery() on relevant chunks
3. Synthesize: aggregate findings, output FINAL(your complete answer here)

To finish: write FINAL(answer) anywhere in your response.
To return a variable: write FINAL_VAR(variable_name).

Rules:
- No import statements — everything is pre-injected
- No network calls (no requests, no urllib)
- Use llmQuery() for semantic reasoning; Python for mechanical chunking/filtering
"""


def _extract_code_blocks(text: str) -> list[str]:
    return re.findall(r"```python\n(.*?)```", text, re.DOTALL)


def _extract_final(text: str) -> Optional[str]:
    m = re.search(r"FINAL\((.+?)\)", text, re.DOTALL)
    return m.group(1).strip() if m else None


def _extract_final_var(text: str) -> Optional[str]:
    m = re.search(r"FINAL_VAR\((\w+)\)", text)
    return m.group(1) if m else None


@click.command()
@click.option("-c", "--context", "context_path", required=True, type=click.Path(exists=True), help="Path to context file")
@click.option("-q", "--query", required=True, help="Question to answer")
@click.option("-m", "--max-iterations", default=10, show_default=True, help="Max REPL iterations")
@click.option("--root-model", default="claude-sonnet-4-5-20250514", show_default=True, help="Orchestrator LLM")
@click.option("--sub-model", default="claude-haiku-4-5-20251001", show_default=True, help="Chunk analysis LLM")
@click.option("--quick", is_flag=True, help="Fast mode: 3 iterations")
def main(context_path: str, query: str, max_iterations: int, root_model: str, sub_model: str, quick: bool) -> None:
    """RLM: analyze large files via recursive LLM+REPL loops."""
    if quick:
        max_iterations = 3

    client = anthropic.Anthropic()

    # Persistent exec namespace — variables survive across iterations
    namespace: dict = {}

    def llm_query(prompt: str) -> str:
        resp = client.messages.create(
            model=sub_model,
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}],
        )
        return resp.content[0].text  # type: ignore[union-attr]

    namespace.update({
        "contextPath": os.path.abspath(context_path),
        "llmQuery": llm_query,
        "open": open,
        "re": re,
        "json": json,
        "os": os,
    })

    messages: list[dict] = []
    answer: Optional[str] = None

    for i in range(max_iterations + 1):
        force_final = i == max_iterations

        if i == 0:
            user_msg = f"Query: {query}\n\nBegin with Recon: read the file, check its size, identify format and chunk boundaries."
        elif force_final:
            user_msg = "Final iteration. Synthesize everything learned and output FINAL(answer) now."
        else:
            user_msg = f"Iteration {i}. Continue analysis or synthesize with FINAL(answer)."

        messages.append({"role": "user", "content": user_msg})
        click.echo(f"[{i}] ", nl=False, err=True)

        resp = client.messages.create(
            model=root_model,
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            messages=messages,
        )
        text: str = resp.content[0].text  # type: ignore[union-attr]
        messages.append({"role": "assistant", "content": text})

        # Check for explicit FINAL answer
        answer = _extract_final(text)
        if answer:
            click.echo("done", err=True)
            break

        # Check for FINAL_VAR
        var_name = _extract_final_var(text)
        if var_name:
            answer = str(namespace.get(var_name, f"<{var_name} not found in namespace>"))
            click.echo("done", err=True)
            break

        # Execute code blocks and capture stdout
        code_blocks = _extract_code_blocks(text)
        all_output: list[str] = []

        for code in code_blocks:
            buf = io.StringIO()
            try:
                with redirect_stdout(buf):
                    exec(compile(code, "<rlm>", "exec"), namespace)  # noqa: S102
                out = buf.getvalue()
            except Exception as exc:
                out = f"Error: {exc}"
            if out:
                all_output.append(out.strip())

        click.echo(f"{len(code_blocks)} block(s)", err=True)

        if all_output:
            combined = "\n".join(all_output)
            messages.append({"role": "user", "content": f"Output:\n{combined}"})
            # FINAL may appear in code output too
            answer = _extract_final(combined)
            if answer:
                break

    if answer is not None:
        click.echo(answer)
    else:
        click.echo("No FINAL answer reached.", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
