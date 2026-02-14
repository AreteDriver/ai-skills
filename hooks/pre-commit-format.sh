#!/usr/bin/env bash
# pre-commit-format.sh — Pre-commit hook that runs format and skill validation.
#
# Installation:
#   cp hooks/pre-commit-format.sh .git/hooks/pre-commit
#   # or symlink:
#   ln -sf ../../hooks/pre-commit-format.sh .git/hooks/pre-commit
#
# This hook runs both validators on staged files. If either fails, the commit
# is blocked with a message explaining what to fix.

set -uo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "Running pre-commit checks..."
echo ""

failed=false

# ─────────────────────────────────────────────
# Check 1: Skill validation
# ─────────────────────────────────────────────
echo "--- Skill validation ---"
if "$REPO_ROOT/tools/validate-skills.sh" 2>/dev/null; then
    echo -e "${GREEN}Skill validation passed${NC}"
else
    echo -e "${RED}Skill validation failed${NC}"
    echo "  Run: ./tools/validate-skills.sh --verbose"
    echo "  Fix: ./tools/validate-skills.sh --fix"
    failed=true
fi
echo ""

# ─────────────────────────────────────────────
# Check 2: Format check
# ─────────────────────────────────────────────
echo "--- Format check ---"
if "$REPO_ROOT/tools/format-check.sh" 2>/dev/null; then
    echo -e "${GREEN}Format check passed${NC}"
else
    echo -e "${RED}Format check failed${NC}"
    echo "  Run: ./tools/format-check.sh --verbose"
    echo "  Fix: ./tools/format-check.sh --fix"
    failed=true
fi
echo ""

# ─────────────────────────────────────────────
# Result
# ─────────────────────────────────────────────
if $failed; then
    echo -e "${RED}Pre-commit checks FAILED${NC} — commit blocked"
    echo ""
    echo "To fix automatically: ./tools/format-check.sh --fix && ./tools/validate-skills.sh --fix"
    echo "To skip (not recommended): git commit --no-verify"
    exit 1
else
    echo -e "${GREEN}All pre-commit checks passed${NC}"
    exit 0
fi
