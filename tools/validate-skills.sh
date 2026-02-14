#!/usr/bin/env bash
# validate-skills.sh — Validates all skills in the ai-skills repository.
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
#   8. Agent registry entries have risk_level and consensus fields
#   9. Agent schema.yaml files have required fields (inputs, outputs, capabilities)
#  10. Bundle references resolve to existing skills

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
            if [ "$dir_basename" = "references" ] || [ "$dir_basename" = "sub-agents" ] || [ "$dir_basename" = "examples" ]; then
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
            warn "$rel_dir is an agent skill without schema.yaml (markdown-only)"
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
# Check 6: Agent registry metadata
# ─────────────────────────────────────────────
echo "--- Check 6: Agent registry metadata ---"
if [ -f "$registry" ]; then
    # Check that agent entries in registry have risk_level and consensus
    if command -v python3 &>/dev/null; then
        python3 - "$registry" "$VERBOSE" <<'PYEOF'
import yaml, sys

registry_path = sys.argv[1]
verbose = sys.argv[2] == "True" if len(sys.argv) > 2 else False
errors = 0
warnings = 0

with open(registry_path) as f:
    reg = yaml.safe_load(f)

agents = reg.get("agents", {})
for category, agent_list in agents.items():
    if not isinstance(agent_list, list):
        continue
    for agent in agent_list:
        name = agent.get("name", "unknown")
        path = f"agents/{category}/{name}"

        if "risk_level" not in agent:
            print(f"WARN: {path} missing 'risk_level' in registry")
            warnings += 1
        elif verbose:
            print(f"PASS: {path} has risk_level={agent['risk_level']}")

        if "consensus" not in agent:
            print(f"WARN: {path} missing 'consensus' in registry")
            warnings += 1
        elif verbose:
            print(f"PASS: {path} has consensus={agent['consensus']}")

        # Validate risk_level values
        valid_risk = {"low", "medium", "high", "critical"}
        if agent.get("risk_level") and agent["risk_level"] not in valid_risk:
            print(f"ERROR: {path} has invalid risk_level '{agent['risk_level']}' (expected: {valid_risk})")
            errors += 1

sys.exit(errors)
PYEOF
        check6_exit=$?
        if [ "$check6_exit" -gt 0 ]; then
            ERRORS=$((ERRORS + check6_exit))
        fi
    else
        pass "Skipping registry metadata check (python3 not available)"
    fi
fi

echo ""

# ─────────────────────────────────────────────
# Check 7: Agent schema.yaml required fields
# ─────────────────────────────────────────────
echo "--- Check 7: Agent schema.yaml structure ---"
if [ -d "$REPO_ROOT/agents" ] && command -v python3 &>/dev/null; then
    while IFS= read -r -d '' schema_file; do
        dir="$(dirname "$schema_file")"
        rel_dir="${dir#$REPO_ROOT/}"

        python3 - "$schema_file" "$rel_dir" "$VERBOSE" <<'PYEOF'
import yaml, sys

schema_path = sys.argv[1]
rel_dir = sys.argv[2]
verbose = sys.argv[3] == "True" if len(sys.argv) > 3 else False

with open(schema_path) as f:
    schema = yaml.safe_load(f)

if not schema:
    print(f"WARN: {rel_dir}/schema.yaml is empty")
    sys.exit(0)

required_sections = ["inputs", "outputs", "capabilities"]
missing = [s for s in required_sections if s not in schema]

if missing:
    print(f"WARN: {rel_dir}/schema.yaml missing sections: {', '.join(missing)}")
else:
    if verbose:
        print(f"PASS: {rel_dir}/schema.yaml has all required sections")
PYEOF
    done < <(find "$REPO_ROOT/agents" -name "schema.yaml" -print0)
fi

echo ""

# ─────────────────────────────────────────────
# Check 8: Bundle references resolve
# ─────────────────────────────────────────────
echo "--- Check 8: Bundle references ---"
bundles_file="$REPO_ROOT/bundles.yaml"
if [ -f "$bundles_file" ] && command -v python3 &>/dev/null; then
    python3 - "$bundles_file" "$REPO_ROOT" "$VERBOSE" <<'PYEOF'
import yaml, sys, os

bundles_path = sys.argv[1]
repo_root = sys.argv[2]
verbose = sys.argv[3] == "True" if len(sys.argv) > 3 else False
errors = 0

with open(bundles_path) as f:
    data = yaml.safe_load(f)

bundles = data.get("bundles", {})
for bundle_name, bundle in bundles.items():
    skills = bundle.get("skills", [])
    for skill_path in skills:
        full_path = os.path.join(repo_root, skill_path)
        if os.path.isdir(full_path) and os.path.isfile(os.path.join(full_path, "SKILL.md")):
            if verbose:
                print(f"PASS: bundle '{bundle_name}' → {skill_path} exists")
        else:
            print(f"ERROR: bundle '{bundle_name}' references {skill_path} which does not exist")
            errors += 1

    hooks = bundle.get("hooks", [])
    for hook_path in hooks:
        full_path = os.path.join(repo_root, hook_path)
        if os.path.isfile(full_path):
            if verbose:
                print(f"PASS: bundle '{bundle_name}' → {hook_path} exists")
        else:
            print(f"ERROR: bundle '{bundle_name}' references hook {hook_path} which does not exist")
            errors += 1

if errors == 0 and verbose:
    print(f"All bundle references valid ({len(bundles)} bundles checked)")
sys.exit(errors)
PYEOF
    check8_exit=$?
    if [ "$check8_exit" -gt 0 ]; then
        ERRORS=$((ERRORS + check8_exit))
    fi
else
    if [ ! -f "$bundles_file" ]; then
        pass "No bundles.yaml found — skipping bundle validation"
    fi
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
