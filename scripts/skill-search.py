#!/usr/bin/env python3
"""Search and discover skills by keyword, tag, or facet.

Usage:
    python3 scripts/skill-search.py "security"
    python3 scripts/skill-search.py --tag python --type persona
    python3 scripts/skill-search.py --fuzzy "reviwer"
    python3 scripts/skill-search.py --info code-reviewer
"""

import argparse
import difflib
import json
import os
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
MANIFESTS_DIR = REPO_ROOT / "manifests"

def load_manifests() -> list[dict[str, Any]]:
    """Load all individual manifest JSONs."""
    manifests = []
    for path in MANIFESTS_DIR.glob("*.json"):
        if path.name == "_index.json":
            continue
        with open(path, "r", encoding="utf-8") as f:
            manifests.append(json.load(f))
    return manifests

def score_skill(skill: dict[str, Any], query: str, fuzzy: bool = False) -> float:
    """Compute a relevance score for a skill against a free-text query.
    Supports multi-keyword queries (space-separated = OR)."""
    tokens = [t.strip() for t in query.lower().split() if len(t.strip()) > 1]
    if not tokens:
        return 0.0
    score = 0.0

    name = skill.get("name", "").lower()
    desc = skill.get("description", "").lower()
    tags = [t.lower() for t in skill.get("tags", [])]
    triggers = [t.lower() for t in skill.get("triggers", [])]
    cat = skill.get("category", "").lower()

    for q in tokens:
        # Name match is highest weight
        if q == name:
            score += 100.0
        elif q in name:
            score += 50.0
        elif fuzzy and difflib.SequenceMatcher(None, q, name).ratio() > 0.7:
            score += 30.0

        # Description match
        if q in desc:
            score += 20.0

        # Tag match
        for tag in tags:
            if q == tag:
                score += 40.0
            elif q in tag:
                score += 25.0

        # Trigger match
        for trig in triggers:
            if q in trig:
                score += 15.0

        # Category match
        if q == cat:
            score += 20.0
        elif q in cat:
            score += 10.0

    return score

def filter_skills(
    skills: list[dict[str, Any]],
    type_filter: str | None = None,
    category_filter: str | None = None,
    tag_filter: str | None = None,
    risk_filter: str | None = None,
) -> list[dict[str, Any]]:
    """Apply facet filters."""
    results = skills
    if type_filter:
        tf = type_filter.lower()
        results = [s for s in results if s.get("type", "").lower() == tf]
    if category_filter:
        cf = category_filter.lower()
        results = [s for s in results if s.get("category", "").lower() == cf]
    if tag_filter:
        tf = tag_filter.lower()
        results = [s for s in results if any(tf == t.lower() for t in s.get("tags", []))]
    if risk_filter:
        rf = risk_filter.lower()
        results = [s for s in results if s.get("risk_level", "").lower() == rf]
    return results

def print_table(skills: list[dict[str, Any]]) -> None:
    """Print a formatted table of skills."""
    if not skills:
        print("No skills found.")
        return

    # Headers
    print(f"{'Name':<25} {'Type':<10} {'Category':<15} {'Score':<8} {'Tags'}")
    print("-" * 120)
    for skill in skills:
        name = skill.get("name", "")
        stype = skill.get("type", "")
        cat = skill.get("category", "")
        score = skill.get("_score", 0.0)
        tags = ", ".join(skill.get("tags", [])[:5])
        print(f"{name:<25} {stype:<10} {cat:<15} {score:<8.1f} {tags}")

def print_info(skill: dict[str, Any]) -> None:
    """Print detailed info about a single skill."""
    print(f"{'='*60}")
    print(f"Skill: {skill.get('name', '')}")
    print(f"Type:  {skill.get('type', '')}")
    print(f"Path:  {skill.get('path', '')}")
    print(f"Desc:  {skill.get('description', '')}")
    print(f"Version: {skill.get('version', '1.0.0')}")
    print(f"Schema: {'yes' if skill.get('has_schema') else 'no'}")
    if skill.get('risk_level'):
        print(f"Risk:  {skill.get('risk_level')}")
    if skill.get('tags'):
        print(f"Tags:  {', '.join(skill['tags'])}")
    if skill.get('triggers'):
        print(f"Triggers: {', '.join(skill['triggers'][:10])}")
    print(f"{'='*60}")

def main() -> int:
    parser = argparse.ArgumentParser(description="Search and discover skills")
    parser.add_argument("query", nargs="?", help="Free-text search query")
    parser.add_argument("--tag", help="Filter by exact tag")
    parser.add_argument("--type", help="Filter by type (persona/agent/workflow)")
    parser.add_argument("--category", help="Filter by category")
    parser.add_argument("--risk", help="Filter by risk level")
    parser.add_argument("--fuzzy", action="store_true", help="Enable fuzzy name matching")
    parser.add_argument("--info", help="Show detailed info for a specific skill name")
    parser.add_argument("--limit", type=int, default=20, help="Max results (default: 20)")
    args = parser.parse_args()

    skills = load_manifests()

    if args.info:
        for skill in skills:
            if skill.get("name") == args.info or skill.get("skill_id") == args.info:
                print_info(skill)
                return 0
        print(f"Skill not found: {args.info}", file=sys.stderr)
        return 1

    # Apply facet filters first
    filtered = filter_skills(
        skills,
        type_filter=args.type,
        category_filter=args.category,
        tag_filter=args.tag,
        risk_filter=args.risk,
    )

    if args.query:
        scored = []
        for skill in filtered:
            s = score_skill(skill, args.query, fuzzy=args.fuzzy)
            if s > 0:
                skill["_score"] = s
                scored.append(skill)
        scored.sort(key=lambda x: x["_score"], reverse=True)
        results = scored[:args.limit]
    else:
        # No query: just list filtered results alphabetically
        results = sorted(filtered, key=lambda x: x.get("name", ""))[:args.limit]

    print_table(results)
    return 0

if __name__ == "__main__":
    sys.exit(main())
