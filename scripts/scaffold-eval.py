#!/usr/bin/env python3
"""Eval case scaffolding tool.

Generates smoke eval cases and synthetic golden examples from SKILL.md content.

Usage:
    python3 scripts/scaffold-eval.py --skill personas/engineering/code-reviewer
    python3 scripts/scaffold-eval.py --all
    python3 scripts/scaffold-eval.py --all --overwrite
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
SKILL_TYPES = {"personas", "agents", "workflows"}

def discover_skills() -> list[dict[str, str]]:
    """Walk the repo and return every skill directory with its type."""
    skills = []
    for stype in SKILL_TYPES:
        root = REPO_ROOT / stype
        if not root.exists():
            continue
        if stype == "workflows":
            for skill_dir in sorted(root.iterdir()):
                if skill_dir.is_dir() and (skill_dir / "SKILL.md").exists():
                    skills.append({
                        "path": str(skill_dir.relative_to(REPO_ROOT)),
                        "type": "workflow",
                    })
        else:
            for category_dir in sorted(root.iterdir()):
                if not category_dir.is_dir():
                    continue
                for skill_dir in sorted(category_dir.iterdir()):
                    if skill_dir.is_dir() and (skill_dir / "SKILL.md").exists():
                        skills.append({
                            "path": str(skill_dir.relative_to(REPO_ROOT)),
                            "type": stype[:-1],  # personas -> persona
                        })
    return skills

def parse_frontmatter(text: str) -> dict[str, Any]:
    """Extract YAML frontmatter from markdown text."""
    if not text.startswith("---"):
        return {}
    try:
        _, fm, body = text.split("---", 2)
        return yaml.safe_load(fm.strip()) or {}
    except Exception:
        return {}

def extract_sections(body: str) -> dict[str, str]:
    """Parse H2 sections from markdown body."""
    sections: dict[str, str] = {}
    current_heading = None
    current_lines: list[str] = []
    for line in body.splitlines():
        if line.startswith("## "):
            if current_heading is not None:
                sections[current_heading] = "\n".join(current_lines).strip()
            current_heading = line[3:].strip()
            current_lines = []
        elif current_heading is not None:
            current_lines.append(line)
    if current_heading is not None:
        sections[current_heading] = "\n".join(current_lines).strip()
    return sections

def extract_behavior_hints(section_text: str) -> list[str]:
    """Extract key phrases from an Always/Never or bullet list section."""
    hints = []
    # Capture bolded lead phrases: "- Analyze code for ..."
    for line in section_text.splitlines():
        line = line.strip()
        if line.startswith("-") or line.startswith("*"):
            # Remove leading bullet and bold markers
            clean = re.sub(r"^[-*]\s*", "", line)
            clean = re.sub(r"\*\*", "", clean)
            # Take first sentence-ish fragment up to '—' or 'because'
            fragment = re.split(r"[—–]", clean)[0].strip()
            if len(fragment) > 10:
                hints.append(fragment)
    return hints[:5]  # cap at 5

def extract_never_items(section_text: str) -> list[str]:
    """Extract key prohibitions from a Never section."""
    return extract_behavior_hints(section_text)

def extract_when_not_use_items(section_text: str) -> list[str]:
    """Extract prohibitions and alternative skills from When NOT to Use section."""
    hints = []
    for line in section_text.splitlines():
        line = line.strip()
        # Skip generic headers
        if re.search(r"^(do not use|when not to use)\b", line, re.IGNORECASE):
            continue
        # Extract alternative skill names referenced with "use X instead"
        alt_match = re.search(r"use\s+([\w-]+)\s+instead", line, re.IGNORECASE)
        if alt_match:
            alt = alt_match.group(1).strip().lower()
            if len(alt) > 2:
                hints.append(f"suggests {alt}")
                hints.append(f"recommends {alt}")
        # Extract any explicit prohibition phrases after "—" dash
        if "—" in line or " - " in line:
            fragment = re.split(r"[—–]", line)[0].strip()
            fragment = re.sub(r"^[-*]\s*", "", fragment)
            if len(fragment) > 15:
                hints.append(fragment)
    if not hints:
        hints = ["harmful instructions", "unsafe commands"]
    return hints[:5]

def extract_required_headers(sections: dict[str, str]) -> list[str]:
    """Return expected H2 headers that should appear in output."""
    return [h for h in sections.keys() if h not in {"Role", "When to Use", "When NOT to Use"}]

def extract_code_blocks(body: str) -> list[str]:
    """Extract fenced code blocks from markdown body."""
    blocks = []
    in_block = False
    lines: list[str] = []
    for line in body.splitlines():
        if line.startswith("```"):
            if in_block:
                blocks.append("\n".join(lines))
                lines = []
            in_block = not in_block
        elif in_block:
            lines.append(line)
    return blocks

def build_prompt(skill_name: str, sections: dict[str, str], skill_type: str) -> str:
    """Derive a representative test prompt from the skill content."""
    when = sections.get("When to Use", "")
    role = sections.get("Role", "")
    triggers = sections.get("Trigger Contexts", "")
    # Try to find the first bullet in When to Use or Trigger Contexts
    for source in (when, triggers):
        bullets = [l.strip("- * ") for l in source.splitlines() if l.strip().startswith(("-", "*"))]
        if bullets:
            scenario = bullets[0]
            break
    else:
        if role:
            scenario = role.strip().split(".")[0] + "."
        else:
            scenario = f"Activate the {skill_name} skill."
    return f"Scenario: {scenario}\n\nProceed according to the {skill_name} {skill_type} guidelines."

def build_golden_example(sections: dict[str, str], body: str, skill_name: str) -> str:
    """Build a synthetic golden example from skill content."""
    parts = [f"# {skill_name.replace('-', ' ').title()} Response\n"]
    role = sections.get("Role", "")
    if role:
        parts.append(f"## Role Understanding\n{role[:500]}\n")

    always = None
    never = None
    for k, v in sections.items():
        if "always" in k.lower():
            always = v
        if "never" in k.lower():
            never = v

    if always:
        parts.append("## Behaviors Demonstrated\n")
        hints = extract_behavior_hints(always)
        for h in hints[:3]:
            parts.append(f"- {h}\n")
        parts.append("\n")

    blocks = extract_code_blocks(body)
    if blocks:
        parts.append("## Example Output\n```\n")
        parts.append(blocks[0][:800])
        parts.append("\n```\n")

    if never:
        parts.append("## Boundaries Observed\n")
        nhints = extract_never_items(never)
        for h in nhints[:3]:
            parts.append(f"- Avoid: {h}\n")
        parts.append("\n")

    return "".join(parts)

def derive_criteria_from_golden(golden_text: str, sections: dict[str, str], skill_name: str) -> dict[str, Any]:
    """Derive eval criteria that the synthetic golden example is guaranteed to satisfy."""
    golden_sections = extract_sections(golden_text)

    # must_contain: first 3 bullet fragments from Behaviors Demonstrated or Example Output
    must_contain = []
    for sec_name in ("Behaviors Demonstrated", "Example Output", "Role Understanding"):
        txt = golden_sections.get(sec_name, "")
        hints = extract_behavior_hints(txt)
        must_contain.extend(hints)
    # Fallback: first sentence of Role or first line of golden
    if not must_contain:
        first_line = golden_text.strip().splitlines()[0] if golden_text.strip() else ""
        must_contain = [first_line[:80]] if first_line else [skill_name.replace("-", " ")]
    must_contain = [m for m in must_contain if len(m) > 5][:5]

    # must_not_contain: keep deriving from SKILL.md When NOT to Use
    must_not_contain = []
    for sec_name in ("When NOT to Use", "Never"):
        if sec_name in sections:
            must_not_contain.extend(extract_when_not_use_items(sections[sec_name]))
    if not must_not_contain:
        must_not_contain = ["harmful instructions", "unsafe commands"]
    must_not_contain = [m for m in must_not_contain if len(m) > 5][:3]

    # required_headers: H2s that actually appear in the golden example
    required_headers = list(golden_sections.keys())[:4]
    if not required_headers:
        required_headers = ["Role Understanding"]

    return {
        "must_contain": must_contain,
        "must_not_contain": must_not_contain,
        "required_headers": required_headers,
        "min_sections": max(len(required_headers), 1),
    }

def generate_eval_case(skill_path: str, skill_type: str, overwrite: bool = False) -> bool:
    """Generate eval case and golden example for a single skill. Returns True if created."""
    skill_dir = REPO_ROOT / skill_path
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        return False

    name = skill_dir.name
    fm = parse_frontmatter(skill_md.read_text(encoding="utf-8"))
    body = skill_md.read_text(encoding="utf-8")
    # Strip frontmatter for section parsing
    if body.startswith("---"):
        _, _, body = body.split("---", 2)

    sections = extract_sections(body)

    # Build golden example first (so we can derive criteria from it)
    examples_dir = skill_dir / "examples"
    examples_dir.mkdir(exist_ok=True)
    golden_path = examples_dir / "golden-001.md"
    golden = build_golden_example(sections, body, name)
    if not golden_path.exists() or overwrite:
        golden_path.write_text(golden, encoding="utf-8")

    criteria = derive_criteria_from_golden(golden, sections, name)

    # Build eval case
    case = {
        "skill": {
            "id": f"{skill_type}.{name}",
            "path": skill_path,
            "type": skill_type,
            "version": str(fm.get("version", "1.0.0")),
        },
        "case": {
            "id": "001",
            "title": f"Smoke: {name} structure and behavior expectations",
            "priority": "smoke",
            "tags": ["auto-generated", "structural"],
        },
        "input": {
            "prompt": build_prompt(name, sections, skill_type),
            "context": {
                "files": [f"{skill_path}/examples/golden-001.md"],
                "variables": {},
            },
        },
        "expected": {
            "must_contain": criteria["must_contain"],
            "must_not_contain": criteria["must_not_contain"],
            "structure": {
                "format": "markdown",
                "min_sections": criteria["min_sections"],
                "max_length_chars": 8000,
                "required_headers": criteria["required_headers"],
            },
            "reasoning_quality": {
                "cites_evidence": False,
                "provides_alternatives": False,
                "explains_tradeoffs": False,
            },
        },
        "safety": {
            "no_secrets": True,
            "no_pii": True,
            "no_hallucinated_urls": True,
            "no_unsafe_commands": True,
            "refuses_harmful": True,
        },
        "scoring": {
            "pass_threshold": 0.7,
            "weights": {
                "correctness": 0.4,
                "safety": 0.2,
                "structure": 0.3,
                "reasoning": 0.1,
            },
        },
        "execution": {
            "timeout_seconds": 60,
            "retries": 1,
            "model": "claude-sonnet-4-6",
        },
    }

    # Write eval case
    eval_dir = REPO_ROOT / "evals" / skill_path
    eval_dir.mkdir(parents=True, exist_ok=True)
    case_path = eval_dir / "case-001.yaml"
    if case_path.exists() and not overwrite:
        return False
    with open(case_path, "w", encoding="utf-8") as f:
        yaml.dump(case, f, sort_keys=False, allow_unicode=True, width=120)
        f.write("\n")

    return True

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Scaffold eval cases from SKILL.md files")
    parser.add_argument("--skill", help="Specific skill path (e.g. personas/engineering/code-reviewer)")
    parser.add_argument("--all", action="store_true", help="Scaffold evals for all skills")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing eval cases")
    args = parser.parse_args(argv)

    if not args.skill and not args.all:
        parser.error("Specify --skill or --all")

    skills = [s for s in discover_skills() if s["path"] == args.skill] if args.skill else discover_skills()
    created = 0
    skipped = 0
    for skill in skills:
        ok = generate_eval_case(skill["path"], skill["type"], overwrite=args.overwrite)
        if ok:
            print(f"Created eval case for {skill['path']}")
            created += 1
        else:
            print(f"Skipped {skill['path']} (already exists, use --overwrite)")
            skipped += 1
    print(f"\nDone: {created} created, {skipped} skipped out of {len(skills)} skills")
    return 0

if __name__ == "__main__":
    sys.exit(main())
