#!/usr/bin/env python3
"""Generate documentation artifacts from registry.

Produces:
- docs/generated/catalog-personas.md — persona catalog table
- docs/generated/catalog-agents.md — agent catalog table
- docs/generated/catalog-workflows.md — workflow catalog table
- docs/generated/counts.md — count summary

Usage:
    python3 scripts/generate-docs.py
"""

import os
import yaml

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(REPO_ROOT, "docs", "generated")


def _load_registry():
    with open(os.path.join(REPO_ROOT, "registry.yaml")) as f:
        return yaml.safe_load(f)


def _generate_persona_table(registry):
    lines = ["# Persona Catalog\n", "| Name | Category | Description | Schema |", "|------|----------|-------------|--------|"]
    for cat, items in sorted(registry.get("personas", {}).items()):
        for item in items:
            name = item["name"]
            desc = item.get("description", "")
            has_schema = "✓" if item.get("has_schema") else ""
            path = item.get("path", "")
            link = f"[{name}](../../{path}/SKILL.md)"
            lines.append(f"| {link} | {cat} | {desc} | {has_schema} |")
    return "\n".join(lines) + "\n"


def _generate_agent_table(registry):
    lines = ["# Agent Catalog\n", "| Name | Category | Description | Risk | Consensus | Schema |", "|------|----------|-------------|------|-----------|--------|"]
    for cat, items in sorted(registry.get("agents", {}).items()):
        for item in items:
            name = item["name"]
            desc = item.get("description", "")
            risk = item.get("risk_level", "")
            consensus = item.get("consensus", "")
            has_schema = "✓" if item.get("has_schema") else ""
            path = item.get("path", "")
            link = f"[{name}](../../{path}/SKILL.md)"
            lines.append(f"| {link} | {cat} | {desc} | {risk} | {consensus} | {has_schema} |")
    return "\n".join(lines) + "\n"


def _generate_workflow_table(registry):
    lines = ["# Workflow Catalog\n", "| Name | Description | Phase | Schema |", "|------|-------------|-------|--------|"]
    for item in sorted(registry.get("workflows", []), key=lambda x: x["name"]):
        name = item["name"]
        desc = item.get("description", "")
        phase = item.get("phase", "")
        has_schema = "✓" if item.get("has_schema") else ""
        path = item.get("path", "")
        link = f"[{name}](../../{path}/SKILL.md)"
        lines.append(f"| {link} | {desc} | {phase} | {has_schema} |")
    return "\n".join(lines) + "\n"


def _generate_counts(registry):
    stats = registry.get("stats", {})
def _generate_search_index(registry):
    lines = ["# Search Index\n", "Alphabetical, faceted index of all skills with tags and triggers.\n"]
    all_items = []
    for cat, items in registry.get("personas", {}).items():
        for item in items:
            item["_type"] = "persona"
            item["_category"] = cat
            all_items.append(item)
    for cat, items in registry.get("agents", {}).items():
        for item in items:
            item["_type"] = "agent"
            item["_category"] = cat
            all_items.append(item)
    for item in registry.get("workflows", []):
        item["_type"] = "workflow"
        item["_category"] = item.get("phase", "general")
        all_items.append(item)

    all_items.sort(key=lambda x: x["name"])

    lines.append("| Name | Type | Category | Tags |")
    lines.append("|------|------|----------|------|")
    for item in all_items:
        name = item["name"]
        path = item.get("path", "")
        link = f"[{name}](../../{path}/SKILL.md)"
        stype = item["_type"]
        cat = item["_category"]
        tags = ", ".join(item.get("tags", [])[:8])
        lines.append(f"| {link} | {stype} | {cat} | {tags} |")

    lines.append("")
    lines.append("## Jump to Type")
    lines.append("")
    lines.append("- [Personas](#personas)")
    lines.append("- [Agents](#agents)")
    lines.append("- [Workflows](#workflows)")
    lines.append("")
    return "\n".join(lines) + "\n"


def _generate_lifecycle_dashboard(registry):
    lines = ["# Lifecycle Dashboard\n", "| Name | Type | Category | Lifecycle | Schema | Examples | Tags |", "|------|------|----------|-----------|--------|----------|------|"]
    all_items = []
    for cat, items in registry.get("personas", {}).items():
        for item in items:
            item["_type"] = "persona"
            item["_category"] = cat
            all_items.append(item)
    for cat, items in registry.get("agents", {}).items():
        for item in items:
            item["_type"] = "agent"
            item["_category"] = cat
            all_items.append(item)
    for item in registry.get("workflows", []):
        item["_type"] = "workflow"
        item["_category"] = item.get("phase", "general")
        all_items.append(item)

    all_items.sort(key=lambda x: (x.get("lifecycle", "experimental"), x["name"]))

    for item in all_items:
        name = item["name"]
        path = item.get("path", "")
        link = f"[{name}](../../{path}/SKILL.md)"
        stype = item["_type"]
        cat = item["_category"]
        life = item.get("lifecycle", "experimental")
        schema = "✓" if item.get("has_schema") else ""
        examples = "✓" if os.path.exists(os.path.join(REPO_ROOT, path, "examples")) else ""
        tags = ", ".join(item.get("tags", [])[:5])
        lines.append(f"| {link} | {stype} | {cat} | {life} | {schema} | {examples} | {tags} |")

    lines.append("")
    return "\n".join(lines) + "\n"


def _generate_counts(registry):
    stats = registry.get("stats", {})
    lines = [
        "# Skill Counts\n",
        f"- **Total skills**: {stats.get('total_skills', 0)}",
        f"- **Personas**: {stats.get('total_personas', 0)}",
        f"- **Agents**: {stats.get('total_agents', 0)}",
        f"- **Workflows**: {stats.get('total_workflows', 0)}",
        "",
        "## By Category\n",
    ]
    cats = stats.get("categories", {})
    for section in ["persona", "agent"]:
        if section in cats:
            lines.append(f"### {section.title()}s")
            for cat, count in sorted(cats[section].items()):
                lines.append(f"- {cat}: {count}")
            lines.append("")
    if "workflow" in cats:
        lines.append(f"### Workflows")
        lines.append(f"- Total: {cats['workflow']}")
    return "\n".join(lines) + "\n"


def generate_docs():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    registry = _load_registry()

    artifacts = {
        "catalog-personas.md": _generate_persona_table(registry),
        "catalog-agents.md": _generate_agent_table(registry),
        "catalog-workflows.md": _generate_workflow_table(registry),
        "counts.md": _generate_counts(registry),
        "search-index.md": _generate_search_index(registry),
        "lifecycle-dashboard.md": _generate_lifecycle_dashboard(registry),
    }

    for filename, content in artifacts.items():
        path = os.path.join(OUTPUT_DIR, filename)
        with open(path, "w") as f:
            f.write("<!-- AUTO-GENERATED from registry.yaml — do not edit manually -->\n")
            f.write("<!-- Run: python3 scripts/generate-docs.py -->\n\n")
            f.write(content)
        print(f"Generated: {path}")

    print(f"\nDone. {len(artifacts)} documentation artifacts generated.")


if __name__ == "__main__":
    generate_docs()
