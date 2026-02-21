#!/usr/bin/env python3
"""Add OpenClaw dual-format metadata to all SKILL.md files.

Walks personas/, agents/, and workflows/ directories, parses YAML frontmatter,
and injects an OpenClaw-compatible `metadata` JSON field. Also adds
`user-invocable: true` for persona skills (slash-command accessible).

Both Claude Code and OpenClaw ignore unknown frontmatter keys, making this safe
for dual-format consumption.

Usage:
    python3 tools/add-openclaw-metadata.py [--dry-run] [--verbose]
"""

import json
import os
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# Emoji mapping by category path
EMOJI_MAP = {
    # Personas
    "personas/engineering": "\U0001f527",      # 🔧
    "personas/data": "\U0001f4ca",             # 📊
    "personas/devops": "\u2699\ufe0f",         # ⚙️
    "personas/claude-code": "\U0001f916",      # 🤖
    "personas/security": "\U0001f6e1\ufe0f",   # 🛡️
    "personas/web": "\U0001f310",              # 🌐
    "personas/api": "\U0001f9ea",              # 🧪
    # Domain sub-categories
    "personas/domain/eve-esi": "\U0001f680",              # 🚀
    "personas/domain/hauling-business-advisor": "\U0001f69b",  # 🚛
    "personas/domain/hauling-image-estimator": "\U0001f69b",
    "personas/domain/hauling-job-scheduler": "\U0001f69b",
    "personas/domain/hauling-lead-qualifier": "\U0001f69b",
    "personas/domain/hauling-quote-generator": "\U0001f69b",
    "personas/domain/gamedev": "\U0001f3ae",              # 🎮
    "personas/domain/tie-dye-business-coach": "\U0001f3a8",  # 🎨
    "personas/domain/apple-dev-best-practices": "\U0001f4f1",  # 📱
    "personas/domain/mentor-linux": "\U0001f427",         # 🐧
    "personas/domain/streamlit": "\U0001f4ca",            # 📊
    "personas/domain/strategic-planner": "\U0001f4cb",    # 📋
    # Agents
    "agents/system": "\U0001f4c1",             # 📁
    "agents/browser": "\U0001f50d",            # 🔍
    "agents/email": "\u2709\ufe0f",            # ✉️
    "agents/integrations": "\U0001f517",       # 🔗
    "agents/orchestration": "\U0001f9e9",      # 🧩
    "agents/analysis": "\U0001f52c",           # 🔬
    # Workflows
    "workflows": "\U0001f4cb",                 # 📋
}

# Per-skill emoji overrides for api category
API_EMOJI_OVERRIDES = {
    "api-tester": "\U0001f9ea",         # 🧪
    "database-ops": "\U0001f5c4\ufe0f", # 🗄️
    "webhook-designer": "\U0001faa9",   # 🪝
    "oauth-integrator": "\U0001f510",   # 🔐
}

ALL_OS = ["darwin", "linux", "win32"]
OPENCLAW_NAME_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")


def get_emoji(skill_path: str, skill_name: str) -> str:
    """Determine the appropriate emoji for a skill based on its path."""
    # Check api overrides first
    if skill_name in API_EMOJI_OVERRIDES:
        return API_EMOJI_OVERRIDES[skill_name]

    # Check specific domain paths (most specific first)
    for prefix, emoji in sorted(EMOJI_MAP.items(), key=lambda x: -len(x[0])):
        if skill_path.startswith(prefix):
            return emoji

    return "\U0001f4e6"  # 📦 fallback


def parse_frontmatter(content: str) -> tuple[str, str, str]:
    """Split SKILL.md into (frontmatter, body, raw_frontmatter_with_delims).

    Returns:
        (frontmatter_text, body_text, full_frontmatter_block)
    """
    if not content.startswith("---\n"):
        raise ValueError("No YAML frontmatter found")

    end_idx = content.index("\n---\n", 4)
    fm_text = content[4:end_idx]
    body = content[end_idx + 5:]  # skip \n---\n
    return fm_text, body, content[:end_idx + 5]


def build_metadata_line(skill_path: str, skill_name: str) -> str:
    """Build the metadata JSON line for a skill."""
    emoji = get_emoji(skill_path, skill_name)
    metadata = {
        "openclaw": {
            "emoji": emoji,
            "os": ALL_OS,
        }
    }
    return f"metadata: {json.dumps(metadata, ensure_ascii=False)}"


def process_skill(skill_md_path: Path, dry_run: bool = False, verbose: bool = False) -> bool:
    """Process a single SKILL.md file, injecting metadata.

    Returns True if the file was modified.
    """
    rel_path = skill_md_path.relative_to(REPO_ROOT)
    skill_dir = rel_path.parent
    skill_path = str(skill_dir)
    skill_name = skill_dir.name

    content = skill_md_path.read_text()

    # Skip if already has metadata
    if "\nmetadata:" in content.split("\n---\n")[0] if "\n---\n" in content else False:
        if verbose:
            print(f"  SKIP {rel_path} (already has metadata)")
        return False

    try:
        fm_text, body, _ = parse_frontmatter(content)
    except (ValueError, IndexError):
        print(f"  ERROR {rel_path}: cannot parse frontmatter")
        return False

    # Validate name matches OpenClaw regex
    name_match = re.search(r"^name:\s*(.+)$", fm_text, re.MULTILINE)
    if name_match:
        name_val = name_match.group(1).strip().strip('"').strip("'")
        if not OPENCLAW_NAME_RE.match(name_val):
            print(f"  WARN {rel_path}: name '{name_val}' doesn't match OpenClaw regex")

    # Build new frontmatter lines
    fm_lines = fm_text.split("\n")
    new_lines = []
    metadata_line = build_metadata_line(skill_path, skill_name)
    metadata_inserted = False
    user_invocable_inserted = False

    is_persona = skill_path.startswith("personas/")

    for line in fm_lines:
        new_lines.append(line)

        # Insert metadata after description line
        if line.startswith("description:") and not metadata_inserted:
            new_lines.append(metadata_line)
            metadata_inserted = True

            # Add user-invocable for persona skills
            if is_persona and not user_invocable_inserted:
                # Check if user-invocable already exists
                if not any(l.startswith("user-invocable:") for l in fm_lines):
                    new_lines.append("user-invocable: true")
                    user_invocable_inserted = True

    if not metadata_inserted:
        # Description not found — append at end
        new_lines.append(metadata_line)
        if is_persona and not any(l.startswith("user-invocable:") for l in fm_lines):
            new_lines.append("user-invocable: true")

    # Reconstruct file
    new_content = "---\n" + "\n".join(new_lines) + "\n---\n" + body

    if dry_run:
        if verbose:
            print(f"  DRY-RUN {rel_path}")
        return True

    skill_md_path.write_text(new_content)
    if verbose:
        print(f"  OK {rel_path}")
    return True


def main() -> int:
    dry_run = "--dry-run" in sys.argv
    verbose = "--verbose" in sys.argv

    if dry_run:
        print("DRY RUN — no files will be modified\n")

    skill_files = sorted(REPO_ROOT.glob("personas/**/SKILL.md"))
    skill_files += sorted(REPO_ROOT.glob("agents/**/SKILL.md"))
    skill_files += sorted(REPO_ROOT.glob("workflows/**/SKILL.md"))

    modified = 0
    total = 0

    for skill_md in skill_files:
        total += 1
        if process_skill(skill_md, dry_run=dry_run, verbose=verbose):
            modified += 1

    print(f"\nProcessed {total} skills, modified {modified}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
