#!/usr/bin/env python3
"""Check eval coverage percentage and fail if below threshold.

Usage:
    python3 scripts/check-eval-coverage.py --threshold 0.90
"""

import argparse
import json
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

def count_skills() -> int:
    """Count total skills from manifests/_index.json or filesystem."""
    index = REPO_ROOT / "manifests" / "_index.json"
    if index.exists():
        data = json.loads(index.read_text())
        return len(data.get("skill_ids", []))
    # Fallback: walk filesystem
    total = 0
    for stype in ("personas", "agents", "workflows"):
        root = REPO_ROOT / stype
        if not root.exists():
            continue
        if stype == "workflows":
            total += sum(1 for d in root.iterdir() if d.is_dir() and (d / "SKILL.md").exists())
        else:
            for cat in root.iterdir():
                if cat.is_dir():
                    total += sum(1 for d in cat.iterdir() if d.is_dir() and (d / "SKILL.md").exists())
    return total

def count_eval_cases() -> int:
    evals_dir = REPO_ROOT / "evals"
    return sum(1 for f in evals_dir.rglob("case-*.yaml"))

def main() -> int:
    parser = argparse.ArgumentParser(description="Check eval coverage")
    parser.add_argument("--threshold", type=float, default=0.90, help="Minimum coverage fraction (0-1)")
    args = parser.parse_args()

    total_skills = count_skills()
    total_evals = count_eval_cases()

    if total_skills == 0:
        print("ERROR: No skills found", file=sys.stderr)
        return 1

    coverage = total_evals / total_skills
    pct = coverage * 100
    status = "PASS" if coverage >= args.threshold else "FAIL"

    print(f"Skills: {total_skills}")
    print(f"Eval cases: {total_evals}")
    print(f"Coverage: {pct:.1f}%")
    print(f"Threshold: {args.threshold * 100:.1f}%")
    print(f"Status: {status}")

    if coverage < args.threshold:
        print(f"::error::Eval coverage {pct:.1f}% is below threshold {args.threshold * 100:.1f}%", file=sys.stderr)
        return 1
    return 0

if __name__ == "__main__":
    sys.exit(main())
