"""Sync external skills from URLs listed in external_skills.txt."""

import re
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import urlopen

import yaml

urls = [
    line.strip()
    for line in Path("external_skills.txt").read_text().splitlines()
    if line.strip() and not line.strip().startswith("#")
]

for url in urls:
    parsed = urlparse(url)
    if parsed.scheme != "https":
        raise ValueError(f"Only HTTPS URLs allowed, got: {url}")

    name = url.rstrip("/").split("/")[-2].lower()
    if not name or name in (".", "..") or not all(c.isalnum() or c in "-_" for c in name):
        raise ValueError(f"Invalid skill name derived from URL: {name!r}")

    dest = Path("skills") / name / "SKILL.md"
    dest.parent.mkdir(parents=True, exist_ok=True)
    print(f"  {name}")
    content = urlopen(url, timeout=10).read().decode()  # noqa: S310
    # Validate frontmatter is parseable YAML
    if content.startswith("---"):
        end = content.index("---", 3)
        yaml.safe_load(content[3:end])
    content = re.sub(r"^(name:\s*)\S+", rf"\1{name}", content, count=1, flags=re.MULTILINE)
    dest.write_text(content)

print(f"Synced {len(urls)} external skills.")
