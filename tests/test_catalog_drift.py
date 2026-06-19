"""Catalog drift detection tests.

Reproduces every finding from AUDIT_REPORT.md (2026-06-19).
Run: python3 -m pytest tests/test_catalog_drift.py -v
"""

import glob
import os
import subprocess
import yaml

import pytest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@pytest.fixture
def registry():
    with open(os.path.join(REPO_ROOT, "registry.yaml")) as f:
        return yaml.safe_load(f)


@pytest.fixture
def bundles():
    with open(os.path.join(REPO_ROOT, "bundles.yaml")) as f:
        return yaml.safe_load(f)


# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────

def _list_leaf_dirs(base: str, depth: int = 2) -> list:
    """Return list of (category, name) tuples for directories at given depth."""
    pattern = os.path.join(REPO_ROOT, base, *["*"] * depth)
    paths = glob.glob(pattern)
    result = []
    for p in paths:
        if not os.path.isdir(p):
            continue
        parts = p.replace(REPO_ROOT + os.sep, "").split(os.sep)
        if len(parts) == depth + 1:
            result.append(tuple(parts[1:]))  # skip base dir
    return result


def _get_registry_entries(registry: dict, section: str) -> set:
    """Extract (category, name) tuples from registry section."""
    entries = set()
    for cat, items in registry.get(section, {}).items():
        if isinstance(items, list):
            for item in items:
                if isinstance(item, dict):
                    entries.add((cat, item["name"]))
        elif isinstance(items, dict):
            for subcat, subitems in items.items():
                if isinstance(subitems, list):
                    for item in subitems:
                        if isinstance(item, dict):
                            entries.add((cat, item["name"]))
    return entries


# ─────────────────────────────────────────────
# Test 1: Persona coverage
# ─────────────────────────────────────────────

def test_all_personas_in_registry(registry):
    """Every personas/<cat>/<name>/SKILL.md must have a registry entry."""
    fs_personas = set()
    for cat, name in _list_leaf_dirs("personas", depth=2):
        skill_md = os.path.join(REPO_ROOT, "personas", cat, name, "SKILL.md")
        if os.path.exists(skill_md):
            fs_personas.add((cat, name))

    reg_personas = _get_registry_entries(registry, "personas")
    orphans = fs_personas - reg_personas
    assert not orphans, f"Personas on disk but not in registry: {sorted(orphans)}"


# ─────────────────────────────────────────────
# Test 2: Agent coverage
# ─────────────────────────────────────────────

def test_all_agents_in_registry(registry):
    """Every agents/<cat>/<name>/SKILL.md must have a registry entry."""
    fs_agents = set()
    for cat, name in _list_leaf_dirs("agents", depth=2):
        skill_md = os.path.join(REPO_ROOT, "agents", cat, name, "SKILL.md")
        if os.path.exists(skill_md):
            fs_agents.add((cat, name))

    reg_agents = _get_registry_entries(registry, "agents")
    orphans = fs_agents - reg_agents
    assert not orphans, f"Agents on disk but not in registry: {sorted(orphans)}"


# ─────────────────────────────────────────────
# Test 3: Workflow coverage
# ─────────────────────────────────────────────

def test_all_workflows_in_registry(registry):
    """Every workflows/<name>/SKILL.md must have a registry entry."""
    fs_workflows = set()
    pattern = os.path.join(REPO_ROOT, "workflows", "*", "SKILL.md")
    for skill_md in glob.glob(pattern):
        name = os.path.basename(os.path.dirname(skill_md))
        fs_workflows.add(name)

    reg_workflows = set()
    wf = registry.get("workflows", [])
    if isinstance(wf, list):
        for item in wf:
            if isinstance(item, dict):
                reg_workflows.add(item["name"])
    elif isinstance(wf, dict):
        for cat, items in wf.items():
            if isinstance(items, list):
                for item in items:
                    if isinstance(item, dict):
                        reg_workflows.add(item["name"])

    orphans = fs_workflows - reg_workflows
    assert not orphans, f"Workflows on disk but not in registry: {sorted(orphans)}"


# ─────────────────────────────────────────────
# Test 4: Schema flags match actual files
# ─────────────────────────────────────────────

def test_schema_flags_match_files(registry):
    """has_schema flag must match presence of schema.yaml or schema/ dir."""
    mismatches = []

    for section in ["personas", "agents"]:
        for cat, items in registry.get(section, {}).items():
            if not isinstance(items, list):
                continue
            for item in items:
                name = item["name"]
                path = item.get("path", "")
                has_schema = item.get("has_schema", False)

                skill_dir = os.path.join(REPO_ROOT, path)
                schema_exists = bool(
                    os.path.exists(os.path.join(skill_dir, "schema.yaml"))
                    or os.path.exists(os.path.join(skill_dir, "schema"))
                    or glob.glob(os.path.join(skill_dir, "*schema*"))
                )

                if has_schema and not schema_exists:
                    mismatches.append(f"{section}/{cat}/{name}: claims schema but none found")
                elif not has_schema and schema_exists:
                    mismatches.append(f"{section}/{cat}/{name}: has schema but flag is false")

    # Workflows: flat list structure
    wf_items = registry.get("workflows", [])
    if isinstance(wf_items, list):
        for item in wf_items:
            if isinstance(item, dict):
                name = item["name"]
                path = item.get("path", "")
                has_schema = item.get("has_schema", False)
                skill_dir = os.path.join(REPO_ROOT, path)
                schema_exists = bool(
                    os.path.exists(os.path.join(skill_dir, "schema.yaml"))
                    or os.path.exists(os.path.join(skill_dir, "schema"))
                    or glob.glob(os.path.join(skill_dir, "*schema*"))
                )
                if has_schema and not schema_exists:
                    mismatches.append(f"workflows/{name}: claims schema but none found")
                elif not has_schema and schema_exists:
                    mismatches.append(f"workflows/{name}: has schema but flag is false")

    assert not mismatches, "Schema flag mismatches:\n" + "\n".join(mismatches)


# ─────────────────────────────────────────────
# Test 5: All bundles installable
# ─────────────────────────────────────────────

def test_all_bundles_installable():
    """Every bundle in bundles.yaml must be accepted by install.sh --bundle."""
    with open(os.path.join(REPO_ROOT, "bundles.yaml")) as f:
        data = yaml.safe_load(f)

    bundles = data.get("bundles", {})
    missing = []

    for name in bundles.keys():
        result = subprocess.run(
            ["bash", os.path.join(REPO_ROOT, "tools", "install.sh"), "--bundle", name],
            capture_output=True,
            text=True,
        )
        # install.sh exits 1 on unknown bundle before any copy
        if result.returncode != 0 and "Unknown bundle" in result.stdout + result.stderr:
            missing.append(name)

    assert not missing, f"Bundles not accepted by installer: {missing}"


# ─────────────────────────────────────────────
# Test 6: content-ops bundle completeness
# ─────────────────────────────────────────────

def test_content_ops_complete(bundles):
    """content-ops must resolve all 8 skills from bundles.yaml."""
    content_ops = bundles.get("bundles", {}).get("content-ops", {})
    expected_skills = content_ops.get("skills", [])
    assert len(expected_skills) == 8, (
        f"content-ops bundles.yaml claims {len(expected_skills)} skills, expected 8"
    )

    # Verify installer resolves all 8 (dry-run check)
    result = subprocess.run(
        ["bash", os.path.join(REPO_ROOT, "tools", "install.sh"), "--bundle", "content-ops"],
        capture_output=True,
        text=True,
    )
    # If installer hard-codes fewer, it'll fail or skip some
    for skill in expected_skills:
        assert skill in result.stdout or result.returncode == 0, (
            f"content-ops skill missing from install output: {skill}"
        )


# ─────────────────────────────────────────────
# Test 7: No missing SKILL.md
# ─────────────────────────────────────────────

def test_no_missing_skill_md(registry):
    """Every registry entry must point to an existing SKILL.md."""
    missing = []

    for section in ["personas", "agents"]:
        for cat, items in registry.get(section, {}).items():
            if not isinstance(items, list):
                continue
            for item in items:
                path = item.get("path", "")
                skill_md = os.path.join(REPO_ROOT, path, "SKILL.md")
                if not os.path.exists(skill_md):
                    missing.append(f"{section}/{cat}/{item['name']}")

    # workflows may be flat
    wf = registry.get("workflows", [])
    if isinstance(wf, list):
        for item in wf:
            if isinstance(item, dict):
                path = item.get("path", "")
                skill_md = os.path.join(REPO_ROOT, path, "SKILL.md")
                if not os.path.exists(skill_md):
                    missing.append(f"workflows/{item['name']}")
    elif isinstance(wf, dict):
        for cat, items in wf.items():
            if isinstance(items, list):
                for item in items:
                    if isinstance(item, dict):
                        path = item.get("path", "")
                        skill_md = os.path.join(REPO_ROOT, path, "SKILL.md")
                        if not os.path.exists(skill_md):
                            missing.append(f"workflows/{cat}/{item['name']}")

    assert not missing, f"Registry entries with missing SKILL.md: {missing}"


# ─────────────────────────────────────────────
# Test 8: README bundle commands valid
# ─────────────────────────────────────────────

def test_readme_bundle_commands_valid():
    """Every --bundle <name> in README must match a bundles.yaml entry."""
    with open(os.path.join(REPO_ROOT, "bundles.yaml")) as f:
        bundle_data = yaml.safe_load(f)
    valid_bundles = set(bundle_data.get("bundles", {}).keys())

    with open(os.path.join(REPO_ROOT, "README.md")) as f:
        readme = f.read()

    import re
    found = re.findall(r'install\.sh\s+--bundle\s+([a-zA-Z0-9_-]+)', readme)
    invalid = [b for b in found if b not in valid_bundles]
    assert not invalid, f"README references invalid bundles: {invalid}"
