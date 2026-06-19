#!/usr/bin/env python3
"""Generate per-skill manifest files from filesystem inventory.

Manifests are the single source of truth for skill metadata.
Registry.yaml and docs are generated from these manifests.

Usage:
    python3 scripts/generate-manifests.py
"""

import glob
import json
import os
import yaml

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANIFESTS_DIR = os.path.join(REPO_ROOT, "manifests")


def _extract_description(skill_dir: str) -> str:
    """Extract description from SKILL.md frontmatter or first paragraph."""
    skill_md = os.path.join(skill_dir, "SKILL.md")
    try:
        with open(skill_md) as f:
            content = f.read()
        if content.startswith("---"):
            fm_end = content.find("---", 3)
            if fm_end > 0:
                fm = yaml.safe_load(content[3:fm_end])
                if isinstance(fm, dict) and "description" in fm:
                    return fm["description"]
        lines = content.splitlines()
        for i, line in enumerate(lines):
            if line.startswith("# "):
                for j in range(i + 1, min(i + 5, len(lines))):
                    if lines[j].strip():
                        return lines[j].strip()
        return ""
    except Exception:
        return ""


def _extract_frontmatter(skill_dir: str) -> dict:
    """Extract full frontmatter from SKILL.md if present."""
    skill_md = os.path.join(skill_dir, "SKILL.md")
    try:
        with open(skill_md) as f:
            content = f.read()
        if content.startswith("---"):
            fm_end = content.find("---", 3)
            if fm_end > 0:
                return yaml.safe_load(content[3:fm_end]) or {}
    except Exception:
        pass
    return {}


def _has_schema(skill_dir: str) -> bool:
    """Check if a skill directory contains schema files."""
    return bool(
        os.path.exists(os.path.join(skill_dir, "schema.yaml"))
        or os.path.exists(os.path.join(skill_dir, "schema"))
        or glob.glob(os.path.join(skill_dir, "*schema*"))
    )


def _generate_skill_id(skill_type: str, category: str, name: str) -> str:
    """Generate a unique skill ID."""
    return f"{skill_type}.{category}.{name}"


def _walk_personas() -> list:
    """Return manifest dicts for all personas."""
    results = []
    for cat_dir in sorted(glob.glob(os.path.join(REPO_ROOT, "personas", "*"))):
        category = os.path.basename(cat_dir)
        for skill_dir in sorted(glob.glob(os.path.join(cat_dir, "*"))):
            if not os.path.isdir(skill_dir):
                continue
            name = os.path.basename(skill_dir)
            if not os.path.exists(os.path.join(skill_dir, "SKILL.md")):
                continue
            frontmatter = _extract_frontmatter(skill_dir)
            results.append({
                "skill_id": _generate_skill_id("persona", category, name),
                "type": "persona",
                "category": category,
                "name": name,
                "path": f"personas/{category}/{name}",
                "description": frontmatter.get("description") or _extract_description(skill_dir) or f"{name.replace('-', ' ').title()} skill",
                "has_schema": _has_schema(skill_dir),
                "has_references": frontmatter.get("has_references", False),
                "version": frontmatter.get("version", "1.0.0"),
            })
    return results


def _walk_agents() -> list:
    """Return manifest dicts for all agents."""
    results = []
    for cat_dir in sorted(glob.glob(os.path.join(REPO_ROOT, "agents", "*"))):
        category = os.path.basename(cat_dir)
        for skill_dir in sorted(glob.glob(os.path.join(cat_dir, "*"))):
            if not os.path.isdir(skill_dir):
                continue
            name = os.path.basename(skill_dir)
            if not os.path.exists(os.path.join(skill_dir, "SKILL.md")):
                continue
            frontmatter = _extract_frontmatter(skill_dir)
            results.append({
                "skill_id": _generate_skill_id("agent", category, name),
                "type": "agent",
                "category": category,
                "name": name,
                "path": f"agents/{category}/{name}",
                "description": frontmatter.get("description") or _extract_description(skill_dir) or f"{name.replace('-', ' ').title()} agent",
                "has_schema": _has_schema(skill_dir),
                "has_references": frontmatter.get("has_references", False),
                "version": frontmatter.get("version", "1.0.0"),
                "risk_level": frontmatter.get("risk_level", "low"),
                "consensus": frontmatter.get("consensus", "none"),
            })
    return results


def _walk_workflows() -> list:
    """Return manifest dicts for all workflows."""
    results = []
    for skill_md in sorted(glob.glob(os.path.join(REPO_ROOT, "workflows", "*", "SKILL.md"))):
        skill_dir = os.path.dirname(skill_md)
        name = os.path.basename(skill_dir)
        frontmatter = _extract_frontmatter(skill_dir)
        results.append({
            "skill_id": _generate_skill_id("workflow", "general", name),
            "type": "workflow",
            "category": "general",
            "name": name,
            "path": f"workflows/{name}",
            "description": frontmatter.get("description") or _extract_description(skill_dir) or f"{name.replace('-', ' ').title()} workflow",
            "has_schema": _has_schema(skill_dir),
            "has_references": frontmatter.get("has_references", False),
            "version": frontmatter.get("version", "1.0.0"),
            "phase": frontmatter.get("phase", "full-lifecycle"),
        })
    return results


def generate_manifests():
    """Generate all manifest files."""
    os.makedirs(MANIFESTS_DIR, exist_ok=True)

    # Clear old manifests
    for old in glob.glob(os.path.join(MANIFESTS_DIR, "*.json")):
        os.remove(old)

    all_manifests = _walk_personas() + _walk_agents() + _walk_workflows()

    # Validate unique IDs
    seen_ids = set()
    duplicates = []
    for m in all_manifests:
        if m["skill_id"] in seen_ids:
            duplicates.append(m["skill_id"])
        seen_ids.add(m["skill_id"])

    if duplicates:
        raise ValueError(f"Duplicate skill IDs found: {duplicates}")

    # Write individual manifest files
    for m in all_manifests:
        filename = m["skill_id"].replace(".", "_") + ".json"
        filepath = os.path.join(MANIFESTS_DIR, filename)
        with open(filepath, "w") as f:
            json.dump(m, f, indent=2)

    # Write index
    index = {
        "generated_at": "auto",
        "total": len(all_manifests),
        "by_type": {
            "persona": len([m for m in all_manifests if m["type"] == "persona"]),
            "agent": len([m for m in all_manifests if m["type"] == "agent"]),
            "workflow": len([m for m in all_manifests if m["type"] == "workflow"]),
        },
        "skill_ids": sorted([m["skill_id"] for m in all_manifests]),
    }
    with open(os.path.join(MANIFESTS_DIR, "_index.json"), "w") as f:
        json.dump(index, f, indent=2)

    print(f"Generated {len(all_manifests)} manifests:")
    print(f"  Personas: {index['by_type']['persona']}")
    print(f"  Agents: {index['by_type']['agent']}")
    print(f"  Workflows: {index['by_type']['workflow']}")


if __name__ == "__main__":
    generate_manifests()
