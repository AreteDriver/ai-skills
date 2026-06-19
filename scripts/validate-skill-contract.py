#!/usr/bin/env python3
"""Validate SKILL.md files against the skill contract v2.

Checks:
- YAML frontmatter has required fields
- Markdown body has required sections
- No secrets in content
- Stable skills have examples/ directory

Usage:
    python3 scripts/validate-skill-contract.py
    python3 scripts/validate-skill-contract.py --json
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent

REQUIRED_FRONTMATTER = {
    "persona": ["name", "description", "lifecycle"],
    "agent": ["name", "version", "description", "type", "category", "lifecycle"],
    "workflow": ["name", "version", "description", "type", "category", "lifecycle"],
}

REQUIRED_SECTIONS = [
    ("## Role", "# Role"),
    ("## When to Use", "## When to use", "# When to Use", "## Usage", "# Usage"),
    ("## When NOT to Use", "## When not to use", "# When NOT to Use", "## When Not to Use"),
    ("## Core Behaviors", "## Behaviors", "## Behavior", "# Core Behaviors", "# Behaviors"),
]

SECRET_PATTERNS = [
    re.compile(r'sk-[a-zA-Z0-9]{20,}'),
    re.compile(r'ghp_[a-zA-Z0-9]{20,}'),
    re.compile(r'sk-ant-[a-zA-Z0-9]{20,}'),
    re.compile(r'[a-zA-Z0-9_-]{20,}\.[a-zA-Z0-9_-]{20,}\.[a-zA-Z0-9_-]{20,}'),
]


def load_skill_md(path: Path) -> tuple[dict[str, Any] | None, str]:
    """Parse YAML frontmatter and markdown body from SKILL.md."""
    text = path.read_text()
    if not text.startswith("---"):
        return None, text

    parts = text.split("---", 2)
    if len(parts) < 3:
        return None, text

    try:
        frontmatter = yaml.safe_load(parts[1])
    except yaml.YAMLError as e:
        return None, text

    body = parts[2]
    return frontmatter, body


def validate_skill(path: Path) -> dict[str, Any]:
    """Validate a single SKILL.md. Returns result dict."""
    rel = str(path.relative_to(REPO_ROOT))
    errors = []
    warnings = []

    frontmatter, body = load_skill_md(path)
    if frontmatter is None:
        errors.append("Missing or malformed YAML frontmatter")
        return {"path": rel, "valid": False, "errors": errors, "warnings": warnings}

    skill_type = frontmatter.get("type", "persona")
    required = REQUIRED_FRONTMATTER.get(skill_type, REQUIRED_FRONTMATTER["persona"])
    for key in required:
        if key not in frontmatter:
            errors.append(f"Missing frontmatter key: {key}")

    lifecycle = frontmatter.get("lifecycle", "")
    if lifecycle and lifecycle not in ("experimental", "beta", "stable", "deprecated"):
        errors.append(f"Invalid lifecycle: '{lifecycle}' (must be experimental, beta, stable, deprecated)")

    for section_group in REQUIRED_SECTIONS:
        section_name = section_group[0].lstrip("# ")
        if not any(alt in body for alt in section_group):
            warnings.append(f"Missing section: {section_name}")

    # Secret scan
    for pat in SECRET_PATTERNS:
        if pat.search(body):
            errors.append("Possible secret leaked in content")
            break

    # Stable skills should have examples/
    skill_dir = path.parent
    examples_dir = skill_dir / "examples"
    if frontmatter.get("lifecycle") == "stable" and not examples_dir.exists():
        warnings.append("Stable skill missing examples/ directory")

    return {
        "path": rel,
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "skill_type": skill_type,
        "name": frontmatter.get("name", "unknown"),
    }


def discover_skills() -> list[Path]:
    skills = []
    for base in ["personas", "agents", "workflows"]:
        for skill_md in (REPO_ROOT / base).rglob("SKILL.md"):
            skills.append(skill_md)
    return sorted(skills)


def main():
    parser = argparse.ArgumentParser(description="Validate SKILL.md files against contract v2")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    args = parser.parse_args()

    skills = discover_skills()
    results = [validate_skill(p) for p in skills]

    total = len(results)
    valid = sum(1 for r in results if r["valid"])
    errors = sum(len(r["errors"]) for r in results)
    warnings = sum(len(r["warnings"]) for r in results)

    if args.json:
        print(json.dumps(results, indent=2))
        return

    print(f"Validated {total} SKILL.md files | {valid} valid | {errors} errors | {warnings} warnings")
    print()

    invalid = [r for r in results if not r["valid"]]
    if invalid:
        print("=== INVALID SKILLS ===")
        for r in invalid:
            print(f"\n{r['path']} ({r['name']})")
            for e in r["errors"]:
                print(f"  ❌ {e}")
            for w in r["warnings"]:
                print(f"  ⚠️  {w}")
        print()

    warned = [r for r in results if r["warnings"] and r["valid"]]
    if warned:
        print("=== WARNINGS ===")
        for r in warned:
            print(f"\n{r['path']} ({r['name']})")
            for w in r["warnings"]:
                print(f"  ⚠️  {w}")
        print()

    if valid < total:
        sys.exit(2)


if __name__ == "__main__":
    main()
