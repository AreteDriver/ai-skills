#!/usr/bin/env python3
"""Extract tags and triggers from SKILL.md content for manifest enrichment.

Usage:
    python3 scripts/extract-tags.py --skill personas/engineering/code-reviewer
    python3 scripts/extract-tags.py --all
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILL_TYPES = {"personas", "agents", "workflows"}

# Known technology vocabulary for fuzzy extraction
TECH_VOCABULARY = {
    "python", "rust", "go", "javascript", "typescript", "java", "kotlin", "swift",
    "c++", "c#", "ruby", "php", "scala", "elixir", "dart", "lua", "shell", "bash",
    "react", "vue", "svelte", "angular", "next.js", "nuxt", "django", "flask",
    "fastapi", "express", "spring", "rails", "laravel", "rails", "fastapi",
    "postgresql", "mysql", "mongodb", "sqlite", "redis", "elasticsearch",
    "docker", "kubernetes", "terraform", "ansible", "aws", "gcp", "azure",
    "ci/cd", "github actions", "gitlab", "jenkins", "circleci", "travis",
    "linux", "macos", "windows", "ios", "android",
    "graphql", "rest", "grpc", "websockets", "oauth", "jwt", "openapi",
    "prometheus", "grafana", "datadog", "new relic", "sentry",
    "tensorflow", "pytorch", "scikit-learn", "pandas", "numpy",
    "blockchain", "smart contract", "solidity", "ethereum", "bitcoin",
    "game dev", "unity", "unreal", "godot", "webgl", "opengl", "vulkan",
    "seo", "a11y", "cms", "e-commerce", "shopify", "stripe",
    "testing", "pytest", "jest", "mocha", "cypress", "playwright", "selenium",
    "eslint", "prettier", "black", "mypy", "ruff", "clang-format",
}

DOMAIN_VOCABULARY = {
    "security", "testing", "frontend", "backend", "api", "devops", "database",
    "web", "mobile", "cloud", "infrastructure", "machine learning", "data",
    "analytics", "visualization", "ci/cd", "deployment", "monitoring",
    "performance", "accessibility", "compliance", "architecture", "design",
    "review", "debugging", "refactoring", "migration", "documentation",
    "seo", "content", "branding", "conversion", "e-commerce",
}

def discover_skills() -> list[tuple[str, str]]:
    """Walk the repo and return every skill (path, type)."""
    skills = []
    for stype in SKILL_TYPES:
        root = REPO_ROOT / stype
        if not root.exists():
            continue
        if stype == "workflows":
            for skill_dir in sorted(root.iterdir()):
                if skill_dir.is_dir() and (skill_dir / "SKILL.md").exists():
                    skills.append((str(skill_dir.relative_to(REPO_ROOT)), "workflow"))
        else:
            for category_dir in sorted(root.iterdir()):
                if not category_dir.is_dir():
                    continue
                for skill_dir in sorted(category_dir.iterdir()):
                    if skill_dir.is_dir() and (skill_dir / "SKILL.md").exists():
                        skills.append((str(skill_dir.relative_to(REPO_ROOT)), stype[:-1]))
    return skills

def parse_frontmatter(text: str) -> dict[str, Any]:
    if not text.startswith("---"):
        return {}
    try:
        _, fm, body = text.split("---", 2)
        return __import__("yaml").safe_load(fm.strip()) or {}
    except Exception:
        return {}

def extract_tags(skill_path: str) -> dict[str, Any]:
    """Read SKILL.md and extract tags, triggers, and technologies."""
    skill_md = REPO_ROOT / skill_path / "SKILL.md"
    if not skill_md.exists():
        return {}
    text = skill_md.read_text(encoding="utf-8")
    body = text
    fm = parse_frontmatter(text)
    if text.startswith("---"):
        try:
            _, _, body = text.split("---", 2)
        except ValueError:
            pass

    tags: set[str] = set()
    triggers: set[str] = set()

    # Category and type as tags
    category = fm.get("category", "")
    if category:
        tags.add(category.lower())
    stype = fm.get("type", "")
    if stype:
        tags.add(stype.lower())

    # Risk level as tag
    risk = fm.get("risk_level", "")
    if risk:
        tags.add(risk.lower())

    # Code fence languages (actual code examples in the skill)
    for match in re.finditer(r"```(\w+)", body):
        lang = match.group(1).lower()
        if len(lang) > 1 and lang not in {"text", "markdown", "md", "yaml", "json"}:
            tags.add(lang)

    # Extract targeted content from relevant sections only
    sections: dict[str, str] = {}
    current_heading = None
    current_lines: list[str] = []
    for line in body.splitlines():
        if line.startswith("## "):
            if current_heading is not None:
                sections[current_heading] = "\n".join(current_lines)
            current_heading = line[3:].strip()
            current_lines = []
        elif current_heading is not None:
            current_lines.append(line)
    if current_heading is not None:
        sections[current_heading] = "\n".join(current_lines)

    # Only scan Core Behaviors, Capabilities, Workflow Steps, Trigger Contexts for tags
    relevant_sections = ["Core Behaviors", "Capabilities", "Workflow Steps", "Trigger Contexts"]
    scan_text = ""
    for sec_name in relevant_sections:
        for key in sections:
            if sec_name.lower() in key.lower():
                scan_text += sections[key] + "\n"

    scan_lower = scan_text.lower()
    for tech in TECH_VOCABULARY:
        # Word-boundary match to avoid substring false positives
        pat = r'\b' + re.escape(tech) + r'\b'
        if re.search(pat, scan_lower):
            tags.add(tech)

    for domain in DOMAIN_VOCABULARY:
        pat = r'\b' + re.escape(domain) + r'\b'
        if re.search(pat, scan_lower):
            tags.add(domain)

    # Trigger extraction from "When to Use" and "Trigger Contexts"
    trigger_text = ""
    for key in sections:
        if "when to use" in key.lower() or "trigger" in key.lower():
            trigger_text += sections[key] + "\n"

    # Extract bullets as triggers
    for line in trigger_text.splitlines():
        stripped = line.strip()
        if stripped.startswith(("-", "*")):
            bullet = re.sub(r"^[-*]\s*", "", stripped)
            if bullet:
                triggers.add(bullet.lower()[:80])

    # Clean up triggers: remove markdown artifacts and bare command lines
    clean_triggers: set[str] = set()
    for t in triggers:
        t_clean = t.strip("*#-–• ")
        # Skip if it's mostly markdown syntax
        if t_clean.startswith("```") or t_clean.endswith("```"):
            continue
        if t_clean.count("*") >= 2 or t_clean.count("#") > 1:
            continue
        # Skip subheading-like lines ending with colon
        if t_clean.endswith(":") and len(t_clean.split()) <= 4:
            continue
        if len(t_clean) >= 3 and len(t_clean) <= 80:
            clean_triggers.add(t_clean)
    triggers = clean_triggers

    # Deduplicate triggers: prefer shorter exact matches
    triggers_sorted = sorted(triggers, key=len, reverse=True)
    final_triggers: set[str] = set()
    for t in triggers_sorted:
        if not any(t != other and t in other for other in final_triggers):
            final_triggers.add(t)

    return {
        "tags": sorted(tags),
        "triggers": sorted(final_triggers)[:20],
    }

def main() -> int:
    parser = argparse.ArgumentParser(description="Extract tags from SKILL.md files")
    parser.add_argument("--skill", help="Specific skill path")
    parser.add_argument("--all", action="store_true", help="Extract for all skills")
    parser.add_argument("--save", action="store_true", help="Write tags into manifest JSON")
    args = parser.parse_args()

    if not args.skill and not args.all:
        parser.error("Specify --skill or --all")

    skills = [(args.skill, "")] if args.skill else discover_skills()
    for path, _ in skills:
        result = extract_tags(path)
        if args.save:
            # Manifest naming convention: {singular_type}_{category}_{name}.json
            p = Path(path)
            singular_type = p.parts[0][:-1] if p.parts[0].endswith("s") else p.parts[0]
            suffix = "_".join(p.parts[1:])
            manifest_path = REPO_ROOT / "manifests" / f"{singular_type}_{suffix}.json"
            if manifest_path.exists():
                data = json.loads(manifest_path.read_text())
                data["tags"] = result["tags"]
                data["triggers"] = result["triggers"]
                manifest_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        else:
            print(f"{path}: {result}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
