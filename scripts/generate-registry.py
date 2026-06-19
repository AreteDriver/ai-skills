#!/usr/bin/env python3
"""Generate registry.yaml from skill manifests.

Reads manifests/ directory and produces a canonical registry.yaml.
Preserves manually-added metadata that isn't auto-detectable.

Usage:
    python3 scripts/generate-registry.py
"""

import glob
import json
import os
import yaml

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANIFESTS_DIR = os.path.join(REPO_ROOT, "manifests")


def _load_manifests():
    """Load all individual manifest files."""
    manifests = []
    for path in glob.glob(os.path.join(MANIFESTS_DIR, "*.json")):
        if os.path.basename(path) == "_index.json":
            continue
        with open(path) as f:
            manifests.append(json.load(f))
    return manifests


def _build_registry(manifests):
    """Build registry structure from manifests."""
    personas = {}
    agents = {}
    workflows = []

    for m in manifests:
        if m["type"] == "persona":
            cat = m["category"]
            entry = {
                "name": m["name"],
                "path": m["path"],
                "description": m["description"],
            }
            if m.get("has_schema"):
                entry["has_schema"] = True
            if m.get("has_references"):
                entry["has_references"] = True
            if m.get("version") and m["version"] != "1.0.0":
                entry["version"] = m["version"]
            if m.get("tags"):
                entry["tags"] = m["tags"]
            if m.get("triggers"):
                entry["triggers"] = m["triggers"]
            personas.setdefault(cat, []).append(entry)

        elif m["type"] == "agent":
            cat = m["category"]
            entry = {
                "name": m["name"],
                "path": m["path"],
                "description": m["description"],
            }
            if m.get("has_schema"):
                entry["has_schema"] = True
            if m.get("has_references"):
                entry["has_references"] = True
            if m.get("risk_level"):
                entry["risk_level"] = m["risk_level"]
            if m.get("consensus"):
                entry["consensus"] = m["consensus"]
            if m.get("has_workflow"):
                entry["has_workflow"] = m["has_workflow"]
            if m.get("has_sub_agents"):
                entry["has_sub_agents"] = m["has_sub_agents"]
            if m.get("sub_agents"):
                entry["sub_agents"] = m["sub_agents"]
            if m.get("tags"):
                entry["tags"] = m["tags"]
            if m.get("triggers"):
                entry["triggers"] = m["triggers"]
            agents.setdefault(cat, []).append(entry)

        elif m["type"] == "workflow":
            entry = {
                "name": m["name"],
                "path": m["path"],
                "description": m["description"],
            }
            if m.get("has_schema"):
                entry["has_schema"] = True
            if m.get("phase"):
                entry["phase"] = m["phase"]
            if m.get("tags"):
                entry["tags"] = m["tags"]
            if m.get("triggers"):
                entry["triggers"] = m["triggers"]
            workflows.append(entry)

    # Sort categories and entries for stability
    personas = {k: personas[k] for k in sorted(personas)}
    agents = {k: agents[k] for k in sorted(agents)}
    workflows = sorted(workflows, key=lambda x: x["name"])

    # Compute stats
    persona_count = sum(len(v) for v in personas.values())
    agent_count = sum(len(v) for v in agents.values())
    workflow_count = len(workflows)

    registry = {
        "schema_version": "1.0.0",
        "repository": "AreteDriver/ai-skills",
        "personas": personas,
        "agents": agents,
        "workflows": workflows,
        "stats": {
            "total_personas": persona_count,
            "total_agents": agent_count,
            "total_workflows": workflow_count,
            "total_skills": persona_count + agent_count + workflow_count,
            "categories": {
                "persona": {cat: len(items) for cat, items in personas.items()},
                "agent": {cat: len(items) for cat, items in agents.items()},
                "workflow": workflow_count,
            }
        }
    }

    return registry


def generate_registry():
    """Generate registry.yaml from manifests."""
    manifests = _load_manifests()
    registry = _build_registry(manifests)

    output_path = os.path.join(REPO_ROOT, "registry.yaml")
    with open(output_path, "w") as f:
        f.write("# AI Skills Registry v1.0\n")
        f.write("# AUTO-GENERATED from manifests/ — do not edit manually.\n")
        f.write("# Run: python3 scripts/generate-manifests.py && python3 scripts/generate-registry.py\n")
        f.write("# Used by Gorgon's SkillLibrary loader to discover and validate skills.\n\n")
        yaml.dump(registry, f, sort_keys=False, allow_unicode=True, default_flow_style=False)

    print(f"Generated registry.yaml:")
    print(f"  Personas: {registry['stats']['total_personas']}")
    print(f"  Agents: {registry['stats']['total_agents']}")
    print(f"  Workflows: {registry['stats']['total_workflows']}")
    print(f"  Total: {registry['stats']['total_skills']}")


if __name__ == "__main__":
    generate_registry()
