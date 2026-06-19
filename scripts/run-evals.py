#!/usr/bin/env python3
"""Behavioral eval runner for ai-skills.

Usage:
    python3 scripts/run-evals.py --skill personas/engineering/code-reviewer
    python3 scripts/run-evals.py --all
    python3 scripts/run-evals.py --report

Loads eval cases from evals/, validates schema, and produces a quality card.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
EVALS_DIR = REPO_ROOT / "evals"
REPORTS_DIR = REPO_ROOT / "evals" / "reports"


def load_eval_case(path: Path) -> dict[str, Any]:
    with open(path, "r") as f:
        return yaml.safe_load(f)


def validate_case(case: dict[str, Any]) -> list[str]:
    """Validate eval case structure. Returns list of error strings."""
    errors = []
    required_top = ["skill", "case", "input", "expected", "safety", "scoring", "execution"]
    for key in required_top:
        if key not in case:
            errors.append(f"Missing top-level key: {key}")

    skill = case.get("skill", {})
    for key in ["id", "path", "type", "version"]:
        if key not in skill:
            errors.append(f"Missing skill.{key}")

    expected = case.get("expected", {})
    if "must_contain" not in expected:
        errors.append("Missing expected.must_contain")
    if "must_not_contain" not in expected:
        errors.append("Missing expected.must_not_contain")

    safety = case.get("safety", {})
    for key in ["no_secrets", "no_pii", "no_hallucinated_urls", "no_unsafe_commands", "refuses_harmful"]:
        if key not in safety:
            errors.append(f"Missing safety.{key}")

    return errors


def score_case(case: dict[str, Any], output_text: str | None) -> dict[str, Any]:
    """Score a single eval case. In this runner, we validate structure only.
    Real execution would send input to a model and check output."""
    expected = case.get("expected", {})
    score = 1.0
    details = []

    if output_text is not None:
        for phrase in expected.get("must_contain", []):
            if phrase.lower() not in output_text.lower():
                score -= 0.1
                details.append(f"Missing required phrase: '{phrase}'")

        for phrase in expected.get("must_not_contain", []):
            if phrase.lower() in output_text.lower():
                score -= 0.1
                details.append(f"Found forbidden phrase: '{phrase}'")
    else:
        details.append("No output provided — structural validation only")

    threshold = case.get("scoring", {}).get("pass_threshold", 1.0)
    passed = score >= threshold

    return {
        "score": round(max(0.0, score), 2),
        "threshold": threshold,
        "passed": passed,
        "details": details,
    }


def run_eval(case_path: Path, output_text: str | None = None) -> dict[str, Any]:
    case = load_eval_case(case_path)
    errors = validate_case(case)
    if errors:
        return {
            "path": str(case_path),
            "valid": False,
            "errors": errors,
            "passed": False,
            "score": 0.0,
        }

    result = score_case(case, output_text)
    return {
        "path": str(case_path),
        "valid": True,
        "skill_id": case["skill"]["id"],
        "case_id": case["case"]["id"],
        "title": case["case"]["title"],
        **result,
    }


def discover_cases(skill_filter: str | None = None) -> list[Path]:
    cases = []
    for case_file in EVALS_DIR.rglob("case-*.yaml"):
        if skill_filter is None or skill_filter in str(case_file):
            cases.append(case_file)
    return sorted(cases)


def generate_report(results: list[dict[str, Any]]) -> str:
    lines = [
        "# Behavioral Eval Quality Card",
        "",
        f"**Total cases:** {len(results)}",
        f"**Passed:** {sum(1 for r in results if r['passed'])}",
        f"**Failed:** {sum(1 for r in results if not r['passed'])}",
        f"**Valid schemas:** {sum(1 for r in results if r.get('valid'))}",
        "",
        "## Results by Skill",
        "",
    ]

    by_skill: dict[str, list[dict[str, Any]]] = {}
    for r in results:
        sid = r.get("skill_id", "unknown")
        by_skill.setdefault(sid, []).append(r)

    for sid, skill_results in sorted(by_skill.items()):
        passed = sum(1 for r in skill_results if r["passed"])
        total = len(skill_results)
        lines.append(f"### {sid}")
        lines.append(f"- **Score:** {passed}/{total}")
        lines.append("")
        for r in skill_results:
            status = "✅ PASS" if r["passed"] else "❌ FAIL"
            lines.append(f"- {status} `{r['case_id']}` — {r['title']} (score: {r['score']})")
            for d in r.get("details", []):
                lines.append(f"  - {d}")
            for e in r.get("errors", []):
                lines.append(f"  - ⚠️ Schema error: {e}")
        lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Run behavioral evals for ai-skills")
    parser.add_argument("--skill", help="Filter to a specific skill path or ID")
    parser.add_argument("--all", action="store_true", help="Run all eval cases")
    parser.add_argument("--report", action="store_true", help="Generate markdown report")
    parser.add_argument("--json", action="store_true", help="Output raw JSON results")
    args = parser.parse_args()

    if not args.skill and not args.all:
        parser.error("Specify --skill <filter> or --all")

    cases = discover_cases(args.skill)
    if not cases:
        print(f"No eval cases found for filter: {args.skill}", file=sys.stderr)
        sys.exit(1)

    results = [run_eval(case) for case in cases]

    if args.json:
        print(json.dumps(results, indent=2))
        return

    if args.report:
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        report_path = REPORTS_DIR / "quality-card.md"
        report = generate_report(results)
        report_path.write_text(report)
        print(f"Report written to {report_path}")

    # Print summary
    total = len(results)
    passed = sum(1 for r in results if r["passed"])
    valid = sum(1 for r in results if r.get("valid"))
    print(f"Ran {total} eval cases | {passed} passed | {total - passed} failed | {valid} valid schemas")

    if passed < total:
        sys.exit(2)


if __name__ == "__main__":
    main()
