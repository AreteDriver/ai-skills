#!/usr/bin/env python3
"""Lifecycle promotion/demotion pipeline for ai-skills.

Usage:
    python3 scripts/lifecycle-manager.py promote personas/engineering/code-reviewer
    python3 scripts/lifecycle-manager.py demote personas/web/compare --reason "missing examples"
    python3 scripts/lifecycle-manager.py audit
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent

def run_validator(skill_path: str) -> dict[str, Any]:
    """Run validate-skill-contract.py on a single skill and return result."""
    import subprocess
    result = subprocess.run(
        [sys.executable, str(REPO_ROOT / "scripts" / "validate-skill-contract.py"), "--json"],
        capture_output=True, text=True
    )
    data = json.loads(result.stdout)
    rel = str(Path(skill_path))
    for item in data:
        if item.get("path") == rel or item.get("path").endswith(rel):
            return item
    return {}

def run_eval(skill_path: str) -> dict[str, Any]:
    """Run eval for a single skill and return result."""
    import subprocess
    result = subprocess.run(
        [sys.executable, str(REPO_ROOT / "scripts" / "run-evals.py"), "--skill", skill_path, "--mode", "golden", "--json"],
        capture_output=True, text=True
    )
    try:
        data = json.loads(result.stdout)
        if data:
            return data[0]
    except json.JSONDecodeError:
        pass
    return {}

def check_gates(skill_path: str) -> tuple[bool, list[str]]:
    """Check promotion gates for a skill. Returns (passes, reasons)."""
    reasons = []
    skill_dir = REPO_ROOT / skill_path
    skill_md = skill_dir / "SKILL.md"

    if not skill_md.exists():
        return False, ["SKILL.md not found"]

    # Gate 1: v2 frontmatter complete
    text = skill_md.read_text(encoding="utf-8")
    if text.startswith("---"):
        try:
            _, fm, _ = text.split("---", 2)
            frontmatter = yaml.safe_load(fm.strip()) or {}
        except Exception:
            frontmatter = {}
    else:
        frontmatter = {}

    required_v2 = {"name", "version", "lifecycle", "description", "type", "category"}
    missing = required_v2 - set(frontmatter.keys())
    if missing:
        reasons.append(f"Missing v2 frontmatter keys: {sorted(missing)}")

    # Gate 2: Has examples/ directory with >=1 file
    examples_dir = skill_dir / "examples"
    if not examples_dir.exists():
        reasons.append("Missing examples/ directory")
    elif not any(examples_dir.iterdir()):
        reasons.append("examples/ directory is empty")

    # Gate 3: Has >=1 eval case that passes
    evals_dir = REPO_ROOT / "evals" / skill_path
    cases = list(evals_dir.glob("case-*.yaml")) if evals_dir.exists() else []
    if not cases:
        reasons.append("No eval cases found")
    else:
        eval_result = run_eval(skill_path)
        if not eval_result.get("passed"):
            reasons.append(f"Eval case failed: {eval_result.get('details', [])}")

    # Gate 4: No validation errors
    val_result = run_validator(str(skill_dir / "SKILL.md"))
    if val_result.get("errors"):
        reasons.append(f"Validation errors: {val_result['errors']}")

    # Gate 5: Not deprecated
    lifecycle = frontmatter.get("lifecycle", "")
    if lifecycle == "deprecated":
        reasons.append("Skill is deprecated")

    return len(reasons) == 0, reasons

def get_all_skills() -> list[str]:
    """Discover all skill paths."""
    skills = []
    for stype in ("personas", "agents", "workflows"):
        root = REPO_ROOT / stype
        if not root.exists():
            continue
        if stype == "workflows":
            for d in sorted(root.iterdir()):
                if d.is_dir() and (d / "SKILL.md").exists():
                    skills.append(str(d.relative_to(REPO_ROOT)))
        else:
            for cat in sorted(root.iterdir()):
                if not cat.is_dir():
                    continue
                for d in sorted(cat.iterdir()):
                    if d.is_dir() and (d / "SKILL.md").exists():
                        skills.append(str(d.relative_to(REPO_ROOT)))
    return skills

def update_lifecycle(skill_path: str, new_state: str) -> None:
    """Update lifecycle in SKILL.md frontmatter."""
    skill_md = REPO_ROOT / skill_path / "SKILL.md"
    text = skill_md.read_text(encoding="utf-8")
    lines = text.splitlines()
    new_lines = []
    found = False
    for line in lines:
        if line.strip().startswith("lifecycle:"):
            new_lines.append(f"lifecycle: {new_state}")
            found = True
        else:
            new_lines.append(line)
    if not found:
        # Insert after version if present
        for i, line in enumerate(new_lines):
            if line.strip().startswith("version:"):
                new_lines.insert(i + 1, f"lifecycle: {new_state}")
                break
    skill_md.write_text("\n".join(new_lines) + "\n", encoding="utf-8")

def audit() -> None:
    """Audit all skills and report promotion/demotion eligibility."""
    skills = get_all_skills()
    promotions = []
    demotions = []
    for skill in skills:
        passes, reasons = check_gates(skill)
        skill_md = REPO_ROOT / skill / "SKILL.md"
        text = skill_md.read_text(encoding="utf-8")
        lifecycle = ""
        if text.startswith("---"):
            try:
                _, fm, _ = text.split("---", 2)
                frontmatter = yaml.safe_load(fm.strip()) or {}
                lifecycle = frontmatter.get("lifecycle", "")
            except Exception:
                pass

        if lifecycle == "experimental" and passes:
            promotions.append((skill, reasons))
        elif lifecycle == "stable" and not passes:
            demotions.append((skill, reasons))

    print("=== PROMOTION CANDIDATES (experimental -> stable) ===")
    if promotions:
        for skill, reasons in promotions:
            print(f"  {skill}")
    else:
        print("  None")
    print(f"  Total: {len(promotions)}")

    print("")
    print("=== DEMOTION CANDIDATES (stable -> experimental) ===")
    if demotions:
        for skill, reasons in demotions:
            print(f"  {skill} — {reasons}")
    else:
        print("  None")
    print(f"  Total: {len(demotions)}")

def promote(skill: str) -> int:
    passes, reasons = check_gates(skill)
    if not passes:
        print(f"Promotion blocked for {skill}:", file=sys.stderr)
        for r in reasons:
            print(f"  - {r}", file=sys.stderr)
        return 1
    update_lifecycle(skill, "stable")
    print(f"Promoted {skill} to stable")
    return 0

def demote(skill: str, reason: str) -> int:
    update_lifecycle(skill, "experimental")
    print(f"Demoted {skill} to experimental — reason: {reason}")
    return 0

def main() -> int:
    parser = argparse.ArgumentParser(description="Lifecycle manager")
    sub = parser.add_subparsers(dest="cmd")
    audit_p = sub.add_parser("audit", help="Scan all skills and report eligibility")
    prom_p = sub.add_parser("promote", help="Promote a skill to stable")
    prom_p.add_argument("skill")
    dem_p = sub.add_parser("demote", help="Demote a skill to experimental")
    dem_p.add_argument("skill")
    dem_p.add_argument("--reason", required=True)
    args = parser.parse_args()

    if args.cmd == "audit":
        audit()
        return 0
    elif args.cmd == "promote":
        return promote(args.skill)
    elif args.cmd == "demote":
        return demote(args.skill, args.reason)
    else:
        parser.print_help()
        return 1

if __name__ == "__main__":
    sys.exit(main())
