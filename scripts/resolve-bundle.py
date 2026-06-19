#!/usr/bin/env python3
"""Resolve bundle definitions from bundles.yaml.

Usage:
    resolve-bundle.py --list              # List all bundle names
    resolve-bundle.py --skills <name>     # Output space-separated skill paths
    resolve-bundle.py --preview <name>    # Output JSON-like preview
    resolve-bundle.py --hooks <name>      # Output space-separated hook paths
"""

import argparse
import json
import os
import sys
import yaml

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    parser = argparse.ArgumentParser(description="Resolve bundle definitions")
    parser.add_argument("--list", action="store_true", help="List bundle names")
    parser.add_argument("--skills", metavar="NAME", help="Get skills for bundle")
    parser.add_argument("--preview", metavar="NAME", help="Get preview for bundle")
    parser.add_argument("--hooks", metavar="NAME", help="Get hooks for bundle")
    args = parser.parse_args()

    bundles_path = os.path.join(REPO_ROOT, "bundles.yaml")
    with open(bundles_path) as f:
        data = yaml.safe_load(f)

    bundles = data.get("bundles", {})

    if args.list:
        for name in sorted(bundles.keys()):
            print(name)
        return

    name = args.skills or args.preview or args.hooks
    if not name:
        parser.error("Specify --skills, --preview, or --hooks")

    if name not in bundles:
        print(f"Unknown bundle: {name}", file=sys.stderr)
        sys.exit(1)

    bundle = bundles[name]

    if args.skills:
        skills = bundle.get("skills", [])
        print(" ".join(skills))

    elif args.hooks:
        hooks = bundle.get("hooks", [])
        print(" ".join(hooks))

    elif args.preview:
        preview = {
            "name": name,
            "description": bundle.get("description", ""),
            "audience": bundle.get("audience", ""),
            "skills": bundle.get("skills", []),
            "hooks": bundle.get("hooks", []),
            "skill_count": len(bundle.get("skills", [])),
            "hook_count": len(bundle.get("hooks", [])),
        }
        print(json.dumps(preview, indent=2))


if __name__ == "__main__":
    main()
