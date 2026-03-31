"""Local tests verifying Codex skill installation.

These validate that `make install` correctly sets up symlinks so Codex
discovers skills via ~/.agents/skills/ and global instructions via
~/.codex/AGENTS.md.

Run with: make test  (or: uv run pytest tests/integration -m local -v)
"""

from pathlib import Path

import frontmatter
import pytest

HOME = Path.home()
CODEX_SKILLS_DIR = HOME / ".agents" / "skills"
CODEX_CONFIG_DIR = HOME / ".codex"
CLAUDE_SKILLS_DIR = HOME / ".claude" / "skills"


@pytest.fixture(autouse=True, scope="module")
def require_install():
    """Fail the module if skills haven't been installed."""
    if not CODEX_SKILLS_DIR.exists():
        pytest.fail("~/.agents/skills/ not found — run 'make install' first")


@pytest.mark.local
def test_codex_agents_md_symlink():
    """~/.codex/AGENTS.md should be a symlink to ~/CLAUDE.md."""
    agents_md = CODEX_CONFIG_DIR / "AGENTS.md"
    assert agents_md.is_symlink(), "~/.codex/AGENTS.md is not a symlink"
    target = agents_md.resolve()
    assert target == (HOME / "CLAUDE.md").resolve(), (
        f"Expected symlink to ~/CLAUDE.md, got {target}"
    )
    assert agents_md.exists(), "~/.codex/AGENTS.md symlink is broken"


@pytest.mark.local
def test_mental_models_skill_installed():
    """mental-models skill should be discoverable by Codex at ~/.agents/skills/."""
    skill_dir = CODEX_SKILLS_DIR / "mental-models"
    assert skill_dir.is_symlink(), "~/.agents/skills/mental-models is not a symlink"
    assert skill_dir.exists(), "~/.agents/skills/mental-models symlink is broken"


@pytest.mark.local
def test_mental_models_skill_md_valid():
    """mental-models SKILL.md should have valid frontmatter Codex can parse."""
    skill_md = CODEX_SKILLS_DIR / "mental-models" / "SKILL.md"
    assert skill_md.exists(), "SKILL.md not found"
    post = frontmatter.loads(skill_md.read_text())
    assert post.metadata.get("name") == "mental-models"
    assert len(post.metadata.get("description", "")) > 20


@pytest.mark.local
def test_codex_skills_match_claude_skills():
    """Every Claude skill should also be available to Codex."""
    if not CLAUDE_SKILLS_DIR.exists():
        pytest.skip("~/.claude/skills/ not found")
    claude_skills = {p.name for p in CLAUDE_SKILLS_DIR.iterdir() if p.is_dir() or p.is_symlink()}
    codex_skills = {p.name for p in CODEX_SKILLS_DIR.iterdir() if p.is_dir() or p.is_symlink()}
    missing = claude_skills - codex_skills
    assert not missing, f"Skills installed for Claude but not Codex: {missing}"


@pytest.mark.local
def test_codex_skill_symlinks_resolve_through_claude():
    """Codex skill symlinks should chain through ~/.claude/skills/ to the repo."""
    skill_link = CODEX_SKILLS_DIR / "mental-models"
    # First hop: ~/.agents/skills/mental-models → ~/.claude/skills/mental-models
    assert skill_link.is_symlink()
    first_target = Path(skill_link.parent / skill_link.readlink()).resolve()
    assert "/.claude/skills/" in str(first_target), (
        f"Expected Codex link to point through ~/.claude/skills/, got {first_target}"
    )
