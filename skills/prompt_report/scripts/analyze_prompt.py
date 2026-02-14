#!/usr/bin/env python3
"""Analyze prompt files for token budget, clarity, and coverage gaps."""

from __future__ import annotations

import json
import re
from dataclasses import asdict
from dataclasses import dataclass
from dataclasses import field
from pathlib import Path

import click
import frontmatter

# Patterns that indicate high-value "signal" content
SIGNAL_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"^\s*-\s+\*\*", re.IGNORECASE),  # bold list items (key terms)
    re.compile(r"^\s*\d+\.\s+", re.IGNORECASE),  # numbered steps (procedure)
    re.compile(r"\b(never|always|must|do not|don't|avoid|require|prohibit)\b", re.IGNORECASE),
    re.compile(r"\b(WHEN|WHEN NOT|IF|THEN|ELSE)\b"),  # conditional logic (caps)
    re.compile(r"```"),  # code blocks (templates/formats)
    re.compile(r"\b(score|formula|ratio|threshold|weight)\b", re.IGNORECASE),
    re.compile(r"^\s*\|.*\|.*\|", re.IGNORECASE),  # table rows
]

# Patterns that indicate lower-value "filler" content
FILLER_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"^\s*-\s+(e\.g\.|for example|for instance)", re.IGNORECASE),
    re.compile(r"^\s*-\s+\(", re.IGNORECASE),  # parenthetical asides
    re.compile(r"\b(note:|tip:|hint:|remember:)", re.IGNORECASE),
    re.compile(r"^\s*<!--"),  # HTML comments
    re.compile(r"\[.*\]\(https?://", re.IGNORECASE),  # markdown links
    re.compile(r"^\s*>\s+", re.IGNORECASE),  # blockquotes (often meta-commentary)
]


@dataclass
class StructureCheck:
    """Result of a single structural check."""

    name: str
    passed: bool
    detail: str = ""


@dataclass
class PromptReport:
    """Analysis report for a single prompt file."""

    file_path: str
    line_count: int = 0
    word_count: int = 0
    char_count: int = 0
    token_estimate: int = 0
    context_pct: float = 0.0
    context_window: int = 200_000

    structure_checks: list[StructureCheck] = field(default_factory=list)

    signal_lines: int = 0
    filler_lines: int = 0
    blank_lines: int = 0
    structural_lines: int = 0  # headers, frontmatter delimiters
    total_content_lines: int = 0

    recommendations: list[str] = field(default_factory=list)

    @property
    def signal_ratio(self) -> float:
        if self.total_content_lines == 0:
            return 0.0
        return self.signal_lines / self.total_content_lines


def _estimate_tokens(text: str) -> int:
    """Estimate token count using chars/4 heuristic."""
    return len(text) // 4


def _is_structural_line(line: str) -> bool:
    """Check if a line is structural (headers, frontmatter delimiters)."""
    stripped = line.strip()
    if stripped.startswith("#"):
        return True
    if stripped == "---":
        return True
    return False


def _classify_line(line: str) -> str:
    """Classify a line as signal, filler, blank, or structural."""
    stripped = line.strip()
    if not stripped:
        return "blank"
    if _is_structural_line(line):
        return "structural"
    for pattern in SIGNAL_PATTERNS:
        if pattern.search(line):
            return "signal"
    for pattern in FILLER_PATTERNS:
        if pattern.search(line):
            return "filler"
    # Default: count as signal (content that doesn't match filler patterns
    # is more likely useful than not)
    return "signal"


def _check_directory_name(file_path: Path, fm_name: str | None) -> StructureCheck:
    """Check if frontmatter name matches directory name."""
    parent = file_path.parent
    if parent.name == "scripts":
        parent = parent.parent
    dir_name = parent.name
    if fm_name is None:
        return StructureCheck("Name matches directory", False, "no name in frontmatter")
    if fm_name == dir_name:
        return StructureCheck("Name matches directory", True)
    return StructureCheck("Name matches directory", False, f"name={fm_name!r}, dir={dir_name!r}")


def analyze_file(file_path: Path, context_window: int = 200_000) -> PromptReport:
    """Analyze a single prompt file."""
    text = file_path.read_text(encoding="utf-8")
    lines = text.splitlines()

    report = PromptReport(
        file_path=str(file_path),
        line_count=len(lines),
        word_count=len(text.split()),
        char_count=len(text),
        token_estimate=_estimate_tokens(text),
        context_window=context_window,
    )
    report.context_pct = (
        (report.token_estimate / context_window) * 100 if context_window > 0 else 0.0
    )

    # Parse frontmatter
    fm_name: str | None = None
    fm_desc: str | None = None
    has_frontmatter = False
    try:
        post = frontmatter.loads(text)
        fm_name = post.metadata.get("name")
        fm_desc = post.metadata.get("description")
        has_frontmatter = bool(post.metadata)
    except Exception:
        pass

    # Structure checks
    report.structure_checks.append(StructureCheck("YAML frontmatter", has_frontmatter))

    has_when = False
    if fm_desc:
        desc_lower = fm_desc.lower()
        has_when = "when" in desc_lower or "use when" in desc_lower
    report.structure_checks.append(StructureCheck("WHEN/WHEN NOT description", has_when))

    under_500 = len(lines) <= 500
    report.structure_checks.append(
        StructureCheck(
            "Under 500 lines",
            under_500,
            f"{len(lines)} lines" if not under_500 else "",
        )
    )

    has_headers = any(line.strip().startswith("#") for line in lines)
    report.structure_checks.append(StructureCheck("Has section headers", has_headers))

    # Only check name match if it looks like a SKILL.md in a skill directory
    if file_path.name == "SKILL.md":
        report.structure_checks.append(_check_directory_name(file_path, fm_name))

    # Classify lines
    for line in lines:
        cls = _classify_line(line)
        if cls == "signal":
            report.signal_lines += 1
        elif cls == "filler":
            report.filler_lines += 1
        elif cls == "blank":
            report.blank_lines += 1
        elif cls == "structural":
            report.structural_lines += 1

    report.total_content_lines = report.signal_lines + report.filler_lines

    # Recommendations
    if not has_frontmatter:
        report.recommendations.append("Add YAML frontmatter with name and description")
    elif not fm_name:
        report.recommendations.append("Add 'name' field to frontmatter")
    if not has_when and fm_desc:
        report.recommendations.append("Add WHEN/WHEN NOT pattern to description")

    if report.line_count > 500:
        report.recommendations.append(
            f"Over 500 lines ({report.line_count}). Consider splitting or compressing."
        )
    elif report.line_count > 150 and report.signal_ratio < 0.5:
        report.recommendations.append(
            f"Compression candidate: {report.line_count} lines with "
            f"{report.signal_ratio:.0%} signal ratio"
        )

    if report.context_pct > 10:
        report.recommendations.append(
            f"Very large prompt ({report.context_pct:.1f}% of context). "
            f"Strongly consider splitting or compressing."
        )
    elif report.context_pct > 5:
        report.recommendations.append(
            f"Large prompt ({report.context_pct:.1f}% of context). "
            f"Ensure value justifies token cost."
        )

    if not has_headers:
        report.recommendations.append("Add section headers for scannability")

    has_numbered_steps = any(re.match(r"^\s*\d+\.\s+", line) for line in lines)
    if not has_numbered_steps and report.line_count > 20:
        report.recommendations.append(
            "No numbered steps found. Consider adding procedural structure."
        )

    return report


def _format_check(check: StructureCheck) -> str:
    """Format a structure check as a line."""
    status = "PASS" if check.passed else "FAIL"
    detail = f" ({check.detail})" if check.detail else ""
    return f"- [{status}] {check.name}{detail}"


def format_text(report: PromptReport) -> str:
    """Format a report as human-readable text."""
    lines: list[str] = []
    lines.append(f"## Prompt Report: {report.file_path}")
    lines.append("")

    lines.append("### Budget")
    lines.append(
        f"- Tokens: ~{report.token_estimate:,} ({report.context_pct:.1f}% of "
        f"{report.context_window:,} context window)"
    )
    lines.append(f"- Lines: {report.line_count} | Words: {report.word_count:,}")
    lines.append("")

    lines.append("### Structure")
    for check in report.structure_checks:
        lines.append(_format_check(check))
    lines.append("")

    lines.append("### Content")
    lines.append(f"- Signal lines: {report.signal_lines} ({report.signal_ratio:.0%})")
    lines.append(f"- Filler lines: {report.filler_lines}")
    lines.append(f"- Blank/structural: {report.blank_lines + report.structural_lines}")
    lines.append("")

    if report.recommendations:
        lines.append("### Recommendations")
        for rec in report.recommendations:
            lines.append(f"- {rec}")
    else:
        lines.append("### Recommendations")
        lines.append("- No issues found.")

    return "\n".join(lines)


def format_json(report: PromptReport) -> str:
    """Format a report as JSON."""
    d = asdict(report)
    d["signal_ratio"] = report.signal_ratio
    return json.dumps(d, indent=2)


@click.command()
@click.argument("files", nargs=-1, required=True, type=click.Path(exists=True))
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["text", "json"]),
    default="text",
    help="Output format.",
)
@click.option(
    "--context-window",
    type=int,
    default=200_000,
    help="Context window size for budget calculation.",
)
def main(files: tuple[str, ...], output_format: str, context_window: int) -> None:
    """Analyze prompt files for token budget, clarity, and coverage gaps."""
    reports: list[PromptReport] = []
    for f in files:
        path = Path(f)
        if not path.is_file():
            click.echo(f"Skipping {f}: not a file", err=True)
            continue
        reports.append(analyze_file(path, context_window))

    if output_format == "json":
        if len(reports) == 1:
            click.echo(format_json(reports[0]))
        else:
            all_data = []
            for r in reports:
                d = asdict(r)
                d["signal_ratio"] = r.signal_ratio
                all_data.append(d)
            click.echo(json.dumps(all_data, indent=2))
    else:
        for i, r in enumerate(reports):
            if i > 0:
                click.echo("\n---\n")
            click.echo(format_text(r))


if __name__ == "__main__":
    main()
