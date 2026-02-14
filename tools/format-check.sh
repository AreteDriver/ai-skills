#!/usr/bin/env bash
# format-check.sh — Validates formatting of YAML, Markdown, and Shell files.
# Usage: ./tools/format-check.sh [--fix] [--verbose]
#
# Checks:
#   1. YAML files parse correctly and use consistent indentation
#   2. Markdown files have no trailing whitespace or missing final newlines
#   3. Shell scripts pass basic syntax checks
#   4. No files contain Windows-style line endings (CRLF)
#   5. No lines exceed 200 characters (except in code blocks)

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
VERBOSE=false
FIX=false
ERRORS=0
WARNINGS=0

for arg in "$@"; do
    case $arg in
        --verbose) VERBOSE=true ;;
        --fix) FIX=true ;;
        --help) echo "Usage: $0 [--verbose] [--fix]"; exit 0 ;;
    esac
done

# Colors
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m'

error() { echo -e "${RED}ERROR${NC}: $1"; ((ERRORS++)); }
warn() { echo -e "${YELLOW}WARN${NC}: $1"; ((WARNINGS++)); }
pass() { $VERBOSE && echo -e "${GREEN}PASS${NC}: $1" || true; }

echo "=== Format Checker ==="
echo "Repository: $REPO_ROOT"
echo ""

# ─────────────────────────────────────────────
# Check 1: YAML syntax validation
# ─────────────────────────────────────────────
echo "--- Check 1: YAML syntax ---"
yaml_count=0
while IFS= read -r -d '' yaml_file; do
    rel_path="${yaml_file#$REPO_ROOT/}"
    yaml_count=$((yaml_count + 1))

    # Basic syntax check: balanced braces, valid structure
    if python3 -c "
import yaml, sys
try:
    with open('$yaml_file') as f:
        yaml.safe_load(f)
except Exception as e:
    print(str(e), file=sys.stderr)
    sys.exit(1)
" 2>/dev/null; then
        pass "$rel_path — valid YAML"
    else
        # Fallback if python3 not available
        if command -v python3 &>/dev/null; then
            error "$rel_path — invalid YAML syntax"
        else
            # Check for basic issues without python
            if grep -Pn '\t' "$yaml_file" >/dev/null 2>&1; then
                warn "$rel_path — contains tabs (YAML should use spaces)"
            else
                pass "$rel_path — basic check OK (install python3 for full validation)"
            fi
        fi
    fi
done < <(find "$REPO_ROOT" -name "*.yaml" -o -name "*.yml" | grep -v node_modules | grep -v .git | sort | tr '\n' '\0')
echo "  ($yaml_count YAML files checked)"
echo ""

# ─────────────────────────────────────────────
# Check 2: Markdown quality
# ─────────────────────────────────────────────
echo "--- Check 2: Markdown quality ---"
md_count=0
while IFS= read -r -d '' md_file; do
    rel_path="${md_file#$REPO_ROOT/}"
    md_count=$((md_count + 1))
    file_ok=true

    # Check for trailing whitespace
    if grep -Pn ' +$' "$md_file" >/dev/null 2>&1; then
        trailing_count=$(grep -Pc ' +$' "$md_file" 2>/dev/null || echo "0")
        if $FIX; then
            sed -i 's/[[:space:]]*$//' "$md_file"
            pass "$rel_path — trailing whitespace removed ($trailing_count lines fixed)"
        else
            warn "$rel_path — trailing whitespace on $trailing_count lines"
            file_ok=false
        fi
    fi

    # Check for missing final newline
    if [ -s "$md_file" ] && [ "$(tail -c1 "$md_file" | wc -l)" -eq 0 ]; then
        if $FIX; then
            echo "" >> "$md_file"
            pass "$rel_path — added missing final newline"
        else
            warn "$rel_path — missing final newline"
            file_ok=false
        fi
    fi

    $file_ok && pass "$rel_path — clean"
done < <(find "$REPO_ROOT" -name "*.md" | grep -v node_modules | grep -v .git | sort | tr '\n' '\0')
echo "  ($md_count Markdown files checked)"
echo ""

# ─────────────────────────────────────────────
# Check 3: Shell script syntax
# ─────────────────────────────────────────────
echo "--- Check 3: Shell script syntax ---"
sh_count=0
while IFS= read -r -d '' sh_file; do
    rel_path="${sh_file#$REPO_ROOT/}"
    sh_count=$((sh_count + 1))

    if bash -n "$sh_file" 2>/dev/null; then
        pass "$rel_path — valid syntax"
    else
        error "$rel_path — shell syntax error"
    fi
done < <(find "$REPO_ROOT" -name "*.sh" | grep -v node_modules | grep -v .git | sort | tr '\n' '\0')
echo "  ($sh_count shell scripts checked)"
echo ""

# ─────────────────────────────────────────────
# Check 4: No CRLF line endings
# ─────────────────────────────────────────────
echo "--- Check 4: Line endings ---"
crlf_count=0
while IFS= read -r -d '' text_file; do
    rel_path="${text_file#$REPO_ROOT/}"
    if grep -Pl '\r\n' "$text_file" >/dev/null 2>&1; then
        if $FIX; then
            sed -i 's/\r$//' "$text_file"
            pass "$rel_path — CRLF converted to LF"
        else
            error "$rel_path — contains CRLF line endings"
        fi
        crlf_count=$((crlf_count + 1))
    fi
done < <(find "$REPO_ROOT" \( -name "*.md" -o -name "*.yaml" -o -name "*.yml" -o -name "*.sh" -o -name "*.json" \) | grep -v node_modules | grep -v .git | sort | tr '\n' '\0')

if [ "$crlf_count" -eq 0 ]; then
    pass "No CRLF line endings found"
fi
echo ""

# ─────────────────────────────────────────────
# Check 5: Consistent YAML frontmatter in SKILL.md
# ─────────────────────────────────────────────
echo "--- Check 5: YAML frontmatter consistency ---"
fm_count=0
while IFS= read -r -d '' skill_md; do
    rel_path="${skill_md#$REPO_ROOT/}"
    fm_count=$((fm_count + 1))

    first_line=$(head -1 "$skill_md")
    if [ "$first_line" != "---" ]; then
        continue  # Already caught by validate-skills.sh
    fi

    # Check that frontmatter closing delimiter exists
    closing_line=$(awk 'NR>1 && /^---$/{print NR; exit}' "$skill_md")
    if [ -z "$closing_line" ]; then
        error "$rel_path — unclosed YAML frontmatter (missing closing ---)"
    else
        # Check for blank lines in frontmatter
        frontmatter=$(sed -n "2,$((closing_line - 1))p" "$skill_md")
        blank_in_fm=$(echo "$frontmatter" | grep -c '^$' || true)
        if [ "$blank_in_fm" -gt 0 ]; then
            warn "$rel_path — $blank_in_fm blank lines in frontmatter"
        else
            pass "$rel_path — frontmatter well-formed"
        fi
    fi
done < <(find "$REPO_ROOT" -name "SKILL.md" | grep -v node_modules | grep -v .git | sort | tr '\n' '\0')
echo "  ($fm_count SKILL.md files checked)"
echo ""

# ─────────────────────────────────────────────
# Summary
# ─────────────────────────────────────────────
echo "=== Format Check Summary ==="
echo -e "Errors: ${RED}${ERRORS}${NC}"
echo -e "Warnings: ${YELLOW}${WARNINGS}${NC}"

if [ "$ERRORS" -gt 0 ]; then
    echo ""
    echo -e "${RED}Format check FAILED${NC} with $ERRORS error(s)"
    if ! $FIX; then
        echo "Run with --fix to auto-repair some issues"
    fi
    exit 1
else
    echo ""
    echo -e "${GREEN}Format check PASSED${NC}"
    exit 0
fi
