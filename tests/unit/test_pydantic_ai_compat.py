"""Verify pydantic-ai API compatibility.

pydantic-ai has renamed AgentRunResult attributes across versions:
  0.0.31: .output
  1.57.0: .data
  1.58.0: .output (reverted)

This test catches regressions when dependabot bumps the version.
"""

import ast
import dataclasses
from pathlib import Path

import pytest
from pydantic_ai.agent import AgentRunResult

SKILLS_DIR = Path(__file__).resolve().parents[2] / "skills"

PYDANTIC_AI_SCRIPTS = sorted(SKILLS_DIR.rglob("*.py"))

# Detect the correct attribute name from the dataclass fields
_RESULT_FIELDS = {f.name for f in dataclasses.fields(AgentRunResult)}
CORRECT_ATTR = "output" if "output" in _RESULT_FIELDS else "data"


def _get_result_attrs(path: Path) -> list[tuple[int, str]]:
    """Find all attribute accesses on variables named 'result' in a Python file."""
    tree = ast.parse(path.read_text())
    attrs = []
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Attribute)
            and isinstance(node.value, ast.Name)
            and node.value.id == "result"
            and node.attr in ("data", "output")
        ):
            attrs.append((node.lineno, node.attr))
    return attrs


class TestPydanticAiCompat:
    def test_agent_run_result_has_correct_field(self) -> None:
        """AgentRunResult must have the expected result field."""
        assert CORRECT_ATTR in _RESULT_FIELDS, (
            f"AgentRunResult fields changed — expected '{CORRECT_ATTR}' but got: {_RESULT_FIELDS}"
        )

    @pytest.mark.parametrize(
        "script",
        [p for p in PYDANTIC_AI_SCRIPTS if _get_result_attrs(p)],
        ids=lambda p: str(p.relative_to(SKILLS_DIR)),
    )
    def test_scripts_use_correct_attr(self, script: Path) -> None:
        """Scripts must use the attribute that actually exists on AgentRunResult."""
        for lineno, attr in _get_result_attrs(script):
            assert attr == CORRECT_ATTR, (
                f"{script.relative_to(SKILLS_DIR)}:{lineno} uses result.{attr} "
                f"but pydantic-ai expects result.{CORRECT_ATTR}"
            )
