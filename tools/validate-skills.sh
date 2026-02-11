#!/usr/bin/env bash
# validate-skills.sh — Validates all skills in the ai_skills repository.
# Usage: ./tools/validate-skills.sh [--verbose] [--fix]
#
# Checks:
#   1. Every skill directory has a SKILL.md
#   2. Every SKILL.md has valid YAML frontmatter (name + description)
#   3. Descriptions are under 300 characters
#   4. Agent skills have a schema.yaml
#   5. Hook scripts are executable
#   6. registry.yaml entries match actual filesystem
#   7. No orphaned skills (on disk but not in registry)

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

echo "=== AI Skills Validator ==="
echo "Repository: $REPO_ROOT"
echo ""

# ─────────────────────────────────────────────
# Check 1: Every skill directory has SKILL.md
# ─────────────────────────────────────────────
echo "--- Check 1: SKILL.md presence ---"
skill_dirs=()

for base_dir in personas agents workflows; do
    if [ -d "$REPO_ROOT/$base_dir" ]; then
        while IFS= read -r -d '' skill_md; do
            dir="$(dirname "$skill_md")"
            rel_dir="${dir#$REPO_ROOT/}"
            skill_dirs+=("$rel_dir")
            pass "$rel_dir/SKILL.md exists"
        done < <(find "$REPO_ROOT/$base_dir" -name "SKILL.md" -print0)
    fi
done

# Find directories that should have SKILL.md but don't
for base_dir in personas agents workflows; do
    if [ -d "$REPO_ROOT/$base_dir" ]; then
        while IFS= read -r -d '' dir; do
            # Skip reference directories and category directories
            dir_basename="$(basename "$dir")"
            if [ "$dir_basename" = "references" ]; then
                continue
            fi

            has_skill_md=false
            if [ -f "$dir/SKILL.md" ]; then
                has_skill_md=true
            fi

            # Check if this is a leaf directory (contains files, not just subdirectories)
            has_files=false
            for f in "$dir"/*; do
                if [ -f "$f" ]; then
                    has_files=true
                    break
                fi
            done

            if $has_files && ! $has_skill_md; then
                rel_dir="${dir#$REPO_ROOT/}"
                error "$rel_dir/ has files but no SKILL.md"
            fi
        done < <(find "$REPO_ROOT/$base_dir" -mindepth 2 -type d -print0)
    fi
done

echo ""

# ─────────────────────────────────────────────
# Check 2: YAML frontmatter validation
# ─────────────────────────────────────────────
echo "--- Check 2: YAML frontmatter ---"
for skill_dir in "${skill_dirs[@]}"; do
    skill_md="$REPO_ROOT/$skill_dir/SKILL.md"

    # Check for frontmatter delimiters
    first_line=$(head -1 "$skill_md")
    if [ "$first_line" != "---" ]; then
        error "$skill_dir/SKILL.md missing YAML frontmatter (no opening ---)"
        continue
    fi

    # Extract frontmatter
    frontmatter=$(sed -n '2,/^---$/p' "$skill_md" | head -n -1)

    # Check for name field
    if ! echo "$frontmatter" | grep -q "^name:"; then
        error "$skill_dir/SKILL.md missing 'name' in frontmatter"
    else
        pass "$skill_dir has name field"
    fi

    # Check for description field
    if ! echo "$frontmatter" | grep -q "^description:"; then
        error "$skill_dir/SKILL.md missing 'description' in frontmatter"
    else
        # Check description length
        desc=$(echo "$frontmatter" | grep "^description:" | sed 's/^description: *//')
        desc_len=${#desc}
        if [ "$desc_len" -gt 300 ]; then
            warn "$skill_dir description is $desc_len chars (max 300)"
        else
            pass "$skill_dir description length OK ($desc_len chars)"
        fi
    fi
done

echo ""

# ─────────────────────────────────────────────
# Check 3: Agent skills have schema.yaml
# ─────────────────────────────────────────────
echo "--- Check 3: Agent schema.yaml ---"
if [ -d "$REPO_ROOT/agents" ]; then
    while IFS= read -r -d '' skill_md; do
        dir="$(dirname "$skill_md")"
        rel_dir="${dir#$REPO_ROOT/}"

        if [ -f "$dir/schema.yaml" ]; then
            pass "$rel_dir has schema.yaml"
        else
            error "$rel_dir is an agent skill but has no schema.yaml"
        fi
    done < <(find "$REPO_ROOT/agents" -name "SKILL.md" -print0)
fi

echo ""

# ─────────────────────────────────────────────
# Check 4: Hook scripts are executable
# ─────────────────────────────────────────────
echo "--- Check 4: Hook executability ---"
if [ -d "$REPO_ROOT/hooks" ]; then
    for hook in "$REPO_ROOT"/hooks/*.sh; do
        if [ -f "$hook" ]; then
            rel_hook="${hook#$REPO_ROOT/}"
            if [ -x "$hook" ]; then
                pass "$rel_hook is executable"
            else
                if $FIX; then
                    chmod +x "$hook"
                    pass "$rel_hook made executable (fixed)"
                else
                    error "$rel_hook is not executable (run with --fix to repair)"
                fi
            fi
        fi
    done
fi

echo ""

# ─────────────────────────────────────────────
# Check 5: Registry consistency
# ─────────────────────────────────────────────
echo "--- Check 5: Registry consistency ---"
registry="$REPO_ROOT/registry.yaml"
if [ -f "$registry" ]; then
    # Extract all paths from registry
    registry_paths=$(grep "path:" "$registry" | sed 's/.*path: *//' | sort)

    # Compare with actual directories
    for path in $registry_paths; do
        if [ -d "$REPO_ROOT/$path" ]; then
            pass "Registry entry $path exists on disk"
        else
            error "Registry entry $path does NOT exist on disk"
        fi
    done

    # Check for orphaned skills (on disk but not in registry)
    for skill_dir in "${skill_dirs[@]}"; do
        if ! echo "$registry_paths" | grep -q "^${skill_dir}$"; then
            warn "$skill_dir exists on disk but is not in registry.yaml"
        fi
    done
else
    warn "registry.yaml not found — skipping consistency check"
fi

echo ""

# ─────────────────────────────────────────────
# Summary
# ─────────────────────────────────────────────
echo "=== Validation Summary ==="
echo "Skills checked: ${#skill_dirs[@]}"
echo -e "Errors: ${RED}${ERRORS}${NC}"
echo -e "Warnings: ${YELLOW}${WARNINGS}${NC}"

if [ "$ERRORS" -gt 0 ]; then
    echo ""
    echo -e "${RED}Validation FAILED${NC} with $ERRORS error(s)"
    exit 1
else
    echo ""
    echo -e "${GREEN}Validation PASSED${NC}"
    exit 0
fi
