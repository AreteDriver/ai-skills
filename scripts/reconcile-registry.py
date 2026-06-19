#!/usr/bin/env python3
"""Reconcile registry.yaml with filesystem inventory.

Preserves existing metadata. Adds missing entries. Fixes schema flags.
Recomputes stats from actual data.
"""

import glob
import os
import yaml

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _load_registry():
    path = os.path.join(REPO_ROOT, "registry.yaml")
    with open(path) as f:
        return yaml.safe_load(f)


def _save_registry(data):
    path = os.path.join(REPO_ROOT, "registry.yaml")
    with open(path, "w") as f:
        yaml.dump(data, f, sort_keys=False, allow_unicode=True, default_flow_style=False)


def _list_personas():
    """Return {(cat, name): path} for all personas with SKILL.md."""
    result = {}
    for cat_dir in glob.glob(os.path.join(REPO_ROOT, "personas", "*")):
        cat = os.path.basename(cat_dir)
        for skill_dir in glob.glob(os.path.join(cat_dir, "*")):
            if os.path.isdir(skill_dir):
                name = os.path.basename(skill_dir)
                if os.path.exists(os.path.join(skill_dir, "SKILL.md")):
                    result[(cat, name)] = f"personas/{cat}/{name}"
    return result


def _list_agents():
    """Return {(cat, name): path} for all agents with SKILL.md."""
    result = {}
    for cat_dir in glob.glob(os.path.join(REPO_ROOT, "agents", "*")):
        cat = os.path.basename(cat_dir)
        for skill_dir in glob.glob(os.path.join(cat_dir, "*")):
            if os.path.isdir(skill_dir):
                name = os.path.basename(skill_dir)
                if os.path.exists(os.path.join(skill_dir, "SKILL.md")):
                    result[(cat, name)] = f"agents/{cat}/{name}"
    return result


def _list_workflows():
    """Return {name: path} for all workflows with SKILL.md."""
    result = {}
    for skill_md in glob.glob(os.path.join(REPO_ROOT, "workflows", "*", "SKILL.md")):
        name = os.path.basename(os.path.dirname(skill_md))
        result[name] = f"workflows/{name}"
    return result


def _has_schema(path):
    """Check if a skill directory contains schema files."""
    skill_dir = os.path.join(REPO_ROOT, path)
    return bool(
        os.path.exists(os.path.join(skill_dir, "schema.yaml"))
        or os.path.exists(os.path.join(skill_dir, "schema"))
        or glob.glob(os.path.join(skill_dir, "*schema*"))
    )


def _extract_description(path):
    """Extract description from SKILL.md frontmatter or first paragraph."""
    skill_md = os.path.join(REPO_ROOT, path, "SKILL.md")
    try:
        with open(skill_md) as f:
            content = f.read()
        # Try frontmatter
        if content.startswith("---"):
            fm_end = content.find("---", 3)
            if fm_end > 0:
                fm = yaml.safe_load(content[3:fm_end])
                if isinstance(fm, dict) and "description" in fm:
                    return fm["description"]
        # Fall back to first paragraph after # heading
        lines = content.splitlines()
        for i, line in enumerate(lines):
            if line.startswith("# "):
                # Look for next non-empty line
                for j in range(i + 1, min(i + 5, len(lines))):
                    if lines[j].strip():
                        return lines[j].strip()
        return ""
    except Exception:
        return ""


def reconcile():
    reg = _load_registry()
    fs_personas = _list_personas()
    fs_agents = _list_agents()
    fs_workflows = _list_workflows()

    # ── Personas ──
    existing_personas = {}
    for cat, items in reg.get("personas", {}).items():
        if not isinstance(items, list):
            continue
        for item in items:
            existing_personas[(cat, item["name"])] = item

    new_personas = {}
    for (cat, name), path in fs_personas.items():
        if (cat, name) in existing_personas:
            # Preserve existing, just fix schema flag
            item = existing_personas[(cat, name)]
            item["has_schema"] = _has_schema(path)
            new_personas.setdefault(cat, []).append(item)
        else:
            # New orphan — add with auto-detected metadata
            desc = _extract_description(path) or f"{name.replace('-', ' ').title()} skill"
            item = {
                "name": name,
                "path": path,
                "description": desc,
                "has_schema": _has_schema(path),
            }
            new_personas.setdefault(cat, []).append(item)

    reg["personas"] = {k: new_personas[k] for k in sorted(new_personas)}

    # ── Agents ──
    existing_agents = {}
    for cat, items in reg.get("agents", {}).items():
        if not isinstance(items, list):
            continue
        for item in items:
            existing_agents[(cat, item["name"])] = item

    new_agents = {}
    for (cat, name), path in fs_agents.items():
        if (cat, name) in existing_agents:
            item = existing_agents[(cat, name)]
            item["has_schema"] = _has_schema(path)
            new_agents.setdefault(cat, []).append(item)
        else:
            desc = _extract_description(path) or f"{name.replace('-', ' ').title()} agent"
            item = {
                "name": name,
                "path": path,
                "description": desc,
                "has_schema": _has_schema(path),
                "risk_level": "low",
                "consensus": "none",
            }
            new_agents.setdefault(cat, []).append(item)

    reg["agents"] = {k: new_agents[k] for k in sorted(new_agents)}

    # ── Workflows ──
    existing_workflows = {}
    wf_list = reg.get("workflows", [])
    if isinstance(wf_list, list):
        for item in wf_list:
            if isinstance(item, dict):
                existing_workflows[item["name"]] = item

    new_workflows = []
    # Fix context-mapper -> context-mapping
    if "context-mapper" in existing_workflows and "context-mapping" not in existing_workflows:
        del existing_workflows["context-mapper"]

    for name, path in sorted(fs_workflows.items()):
        if name in existing_workflows:
            item = existing_workflows[name]
            item["has_schema"] = _has_schema(path)
            new_workflows.append(item)
        else:
            desc = _extract_description(path) or f"{name.replace('-', ' ').title()} workflow"
            item = {
                "name": name,
                "path": path,
                "description": desc,
                "has_schema": _has_schema(path),
                "phase": "full-lifecycle",
            }
            new_workflows.append(item)

    reg["workflows"] = new_workflows

    # ── Recompute stats ──
    persona_count = sum(len(v) for v in reg["personas"].values())
    agent_count = sum(len(v) for v in reg["agents"].values())
    workflow_count = len(reg["workflows"])

    reg["stats"] = {
        "total_personas": persona_count,
        "total_agents": agent_count,
        "total_workflows": workflow_count,
        "total_skills": persona_count + agent_count + workflow_count,
        "categories": {
            "persona": {cat: len(items) for cat, items in reg["personas"].items()},
            "agent": {cat: len(items) for cat, items in reg["agents"].items()},
            "workflow": workflow_count,
        }
    }

    _save_registry(reg)
    print(f"Reconciled registry:")
    print(f"  Personas: {persona_count}")
    print(f"  Agents: {agent_count}")
    print(f"  Workflows: {workflow_count}")
    print(f"  Total: {persona_count + agent_count + workflow_count}")


if __name__ == "__main__":
    reconcile()
