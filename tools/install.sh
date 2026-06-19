#!/usr/bin/env bash
# install.sh — Install ai-skills personas, agents, hooks, and bundles.
# Usage:
#   ./tools/install.sh --all                    Install everything
#   ./tools/install.sh --persona code-reviewer  Install one persona
#   ./tools/install.sh --bundle webapp-security Install a curated bundle
#   ./tools/install.sh --list                   List available skills and bundles
#   ./tools/install.sh --uninstall [<bundle>]    Remove installed skills (all, or specific bundle)
#
# Installs to ~/.claude/skills/ by default (override with CLAUDE_SKILLS_DIR).

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SKILLS_DIR="${CLAUDE_SKILLS_DIR:-$HOME/.claude/skills}"
HOOKS_DIR="${CLAUDE_HOOKS_DIR:-$HOME/.claude/hooks}"
MANIFESTS_DIR="${AI_SKILLS_MANIFESTS_DIR:-$HOME/.ai-skills/manifests}"
SYMLINK=false
DRY_RUN=false
PREVIEW=false
ACTION=""
TARGET=""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m'

usage() {
    cat <<'EOF'
AI Skills Installer

USAGE:
    ./tools/install.sh [OPTIONS] ACTION

ACTIONS:
    --all                       Install all personas + agents + workflows + hooks
    --persona <name>            Install a single persona skill
    --agent <name>              Install a single agent skill
    --workflow <name>           Install a single workflow skill
    --bundle <name>             Install a curated bundle
    --hooks                     Install all hook scripts
    --list                      List available skills and bundles
    --uninstall [<bundle>]        Remove installed skills (all, or specific bundle)

OPTIONS:
    --symlink                   Symlink instead of copy (for development)
    --dry-run                   Show what would be installed without copying
    --preview                   Show bundle contents before installing
    --dir <path>                Override install directory (default: ~/.claude/skills)
    --help                      Show this help

BUNDLES:
    webapp-security             code-reviewer + security-auditor + testing-specialist
    release-engineering         release-engineer + code-reviewer + cicd-pipeline
    data-pipeline               data-engineer + data-analyst + data-visualizer + report-generator
    full-stack-dev              senior-software-engineer + code-reviewer + testing-specialist + software-architect
    claude-code-dev             hooks-designer + plugin-builder + mcp-server-builder + cicd-pipeline
    website-builder             Full website lifecycle (8 skills: frontend, backend, deploy, design, SEO, analytics, perf, security)
    website-ecommerce           E-commerce sites (5 skills: frontend, merchant, content, SEO, deploy)
    website-content             Content-driven sites (5 skills: CMS, content, SEO, analytics, design)
    api-integration             API lifecycle (4 skills: api-tester, database-ops, webhook-designer, oauth-integrator)

EXAMPLES:
    ./tools/install.sh --list
    ./tools/install.sh --bundle webapp-security
    ./tools/install.sh --persona code-reviewer --symlink
    ./tools/install.sh --all
EOF
    exit 0
}

# ─────────────────────────────────────────────
# Bundle resolution (delegated to Python for YAML parsing)
# ─────────────────────────────────────────────
BUNDLE_RESOLVER="$REPO_ROOT/scripts/resolve-bundle.py"

bundle_skills() {
    python3 "$BUNDLE_RESOLVER" --skills "$1" 2>/dev/null
}

bundle_hooks() {
    python3 "$BUNDLE_RESOLVER" --hooks "$1" 2>/dev/null
}

bundle_list() {
    python3 "$BUNDLE_RESOLVER" --list 2>/dev/null
}

bundle_preview() {
    python3 "$BUNDLE_RESOLVER" --preview "$1" 2>/dev/null
}

bundle_exists() {
    python3 "$BUNDLE_RESOLVER" --skills "$1" >/dev/null 2>&1
}

# ─────────────────────────────────────────────
# Parse arguments
# ─────────────────────────────────────────────
while [[ $# -gt 0 ]]; do
    case $1 in
        --all)       ACTION="all"; shift ;;
        --persona)   ACTION="persona"; TARGET="$2"; shift 2 ;;
        --agent)     ACTION="agent"; TARGET="$2"; shift 2 ;;
        --workflow)  ACTION="workflow"; TARGET="$2"; shift 2 ;;
        --bundle)    ACTION="bundle"; TARGET="$2"; shift 2 ;;
        --hooks)     ACTION="hooks"; shift ;;
        --list)      ACTION="list"; shift ;;
        --uninstall) ACTION="uninstall"; TARGET="$2"; shift 2 ;;
        --symlink)   SYMLINK=true; shift ;;
        --dry-run)   DRY_RUN=true; shift ;;
        --preview)   PREVIEW=true; shift ;;
        --dir)       SKILLS_DIR="$2"; shift 2 ;;
        --help)      usage ;;
        *) echo -e "${RED}Unknown option: $1${NC}"; usage ;;
    esac
done

if [ -z "$ACTION" ]; then
    usage
fi

# ─────────────────────────────────────────────
# Helper functions
# ─────────────────────────────────────────────
install_skill() {
    local src="$1"
    local skill_name
    skill_name="$(basename "$src")"
    local dest="$SKILLS_DIR/$skill_name"

    if [ ! -d "$REPO_ROOT/$src" ]; then
        echo -e "  ${RED}✗${NC} $src — not found"
        return 1
    fi

    if $DRY_RUN; then
        echo -e "  ${BLUE}∼${NC} $skill_name → would install to $dest"
        return 0
    fi

    # Remove existing
    if [ -e "$dest" ] || [ -L "$dest" ]; then
        rm -rf "$dest"
    fi

    if $SYMLINK; then
        ln -s "$REPO_ROOT/$src" "$dest"
        echo -e "  ${GREEN}✓${NC} $skill_name → linked"
    else
        cp -r "$REPO_ROOT/$src" "$dest"
        echo -e "  ${GREEN}✓${NC} $skill_name → installed"
    fi
}

install_hooks() {
    mkdir -p "$HOOKS_DIR"
    local count=0
    for hook in "$REPO_ROOT"/hooks/*.sh; do
        if [ -f "$hook" ]; then
            local hook_name
            hook_name="$(basename "$hook")"
            local dest="$HOOKS_DIR/$hook_name"

            if $SYMLINK; then
                ln -sf "$hook" "$dest"
            else
                cp "$hook" "$dest"
                chmod +x "$dest"
            fi
            count=$((count + 1))
        fi
    done
    echo -e "  ${GREEN}✓${NC} $count hooks installed to $HOOKS_DIR"
}

find_skill() {
    local name="$1"
    local type="$2"  # personas, agents, or workflows

    # Search across all categories
    local found=""
    while IFS= read -r -d '' skill_md; do
        local dir
        dir="$(dirname "$skill_md")"
        local dir_basename
        dir_basename="$(basename "$dir")"
        if [ "$dir_basename" = "$name" ]; then
            found="${dir#$REPO_ROOT/}"
            break
        fi
    done < <(find "$REPO_ROOT/$type" -name "SKILL.md" -print0 2>/dev/null)

    echo "$found"
}

write_manifest() {
    local bundle_name="$1"
    local skills="$2"
    local hooks="$3"
    local timestamp
    timestamp="$(date -u +%Y%m%d-%H%M%S)"
    local manifest_file="$MANIFESTS_DIR/${bundle_name}-${timestamp}.json"

    mkdir -p "$MANIFESTS_DIR"

    # Build JSON manifest
    {
        echo "{"
        echo "  \"bundle\": \"$bundle_name\","
        echo "  \"installed_at\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\","
        echo "  \"skills_dir\": \"$SKILLS_DIR\","
        echo "  \"skills\": ["
        local first=true
        for skill_path in $skills; do
            local skill_name
            skill_name="$(basename "$skill_path")"
            if [ "$first" = true ]; then
                first=false
            else
                echo ","
            fi
            echo -n "    {\"source\": \"$REPO_ROOT/$skill_path\", \"dest\": \"$SKILLS_DIR/$skill_name\"}"
        done
        echo ""
        echo "  ],"
        echo "  \"hooks\": ["
        first=true
        for hook in $hooks; do
            if [ "$first" = true ]; then
                first=false
            else
                echo ","
            fi
            echo -n "    \"$hook\""
        done
        echo ""
        echo "  ]"
        echo "}"
    } > "$manifest_file"

    echo -e "  ${BLUE}ℹ${NC} Manifest written to $manifest_file"
}

uninstall_bundle() {
    local bundle_name="$1"
    local manifest_pattern="$MANIFESTS_DIR/${bundle_name}-*.json"
    local manifests
    manifests="$(ls -1 $manifest_pattern 2>/dev/null | sort -r)"

    if [ -z "$manifests" ]; then
        echo -e "${RED}No manifest found for bundle: $bundle_name${NC}"
        echo "  Installed bundles with manifests:"
        for mf in "$MANIFESTS_DIR"/*-*.json; do
            if [ -f "$mf" ]; then
                local bn
                bn="$(basename "$mf" | sed 's/-[0-9]\{8\}-[0-9]\{6\}\.json$//')"
                echo "    - $bn"
            fi
        done 2>/dev/null
        exit 1
    fi

    # Use the most recent manifest
    local manifest_file
    manifest_file="$(echo "$manifests" | head -1)"

    echo -e "${BOLD}Uninstalling bundle: $bundle_name${NC}"
    echo -e "  Using manifest: $(basename "$manifest_file")"

    # Parse and remove files (naive JSON parsing — skill dest paths contain "dest":)
    local removed=0
    local dest_paths
    dest_paths="$(grep '"dest":' "$manifest_file" | sed 's/.*"dest": *"\([^"]*\)".*/\1/')"

    for dest in $dest_paths; do
        if [ -e "$dest" ] || [ -L "$dest" ]; then
            rm -rf "$dest"
            echo -e "  ${GREEN}✓${NC} Removed $(basename "$dest")"
            removed=$((removed + 1))
        fi
    done

    # Remove the manifest itself
    rm -f "$manifest_file"

    echo ""
    echo -e "${GREEN}Uninstalled $removed skills from bundle '$bundle_name'${NC}"
}

# ─────────────────────────────────────────────
# Actions
# ─────────────────────────────────────────────
case $ACTION in
    list)
        echo -e "${BOLD}Available Personas:${NC}"
        for base_dir in personas/engineering personas/data personas/devops personas/claude-code personas/security personas/domain personas/api personas/web; do
            if [ -d "$REPO_ROOT/$base_dir" ]; then
                category="$(basename "$base_dir")"
                echo -e "  ${BLUE}$category:${NC}"
                for skill_dir in "$REPO_ROOT/$base_dir"/*/; do
                    if [ -f "$skill_dir/SKILL.md" ]; then
                        skill_name="$(basename "$skill_dir")"
                        desc=$(sed -n '/^description:/s/^description: *//p' "$skill_dir/SKILL.md" 2>/dev/null | head -1)
                        printf "    %-30s %s\n" "$skill_name" "$desc"
                    fi
                done
            fi
        done

        echo ""
        echo -e "${BOLD}Available Agents:${NC}"
        for base_dir in agents/system agents/browser agents/email agents/integrations agents/orchestration agents/analysis; do
            if [ -d "$REPO_ROOT/$base_dir" ]; then
                category="$(basename "$base_dir")"
                echo -e "  ${BLUE}$category:${NC}"
                for skill_dir in "$REPO_ROOT/$base_dir"/*/; do
                    if [ -f "$skill_dir/SKILL.md" ]; then
                        skill_name="$(basename "$skill_dir")"
                        desc=$(sed -n '/^description:/s/^description: *//p' "$skill_dir/SKILL.md" 2>/dev/null | head -1)
                        printf "    %-30s %s\n" "$skill_name" "$desc"
                    fi
                done
            fi
        done

        echo ""
        echo -e "${BOLD}Available Workflows:${NC}"
        if [ -d "$REPO_ROOT/workflows" ]; then
            for skill_dir in "$REPO_ROOT/workflows"/*/; do
                if [ -f "$skill_dir/SKILL.md" ]; then
                    skill_name="$(basename "$skill_dir")"
                    desc=$(sed -n '/^description:/s/^description: *//p' "$skill_dir/SKILL.md" 2>/dev/null | head -1)
                    printf "  %-30s %s\n" "$skill_name" "$desc"
                fi
            done
        fi

        echo ""
        echo -e "${BOLD}Available Bundles:${NC}"
        while IFS= read -r bundle_name; do
            skills="$(bundle_skills "$bundle_name")"
            count=$(echo "$skills" | wc -w)
            skill_names=$(echo "$skills" | tr ' ' '\n' | xargs -I{} basename {} | tr '\n' ', ' | sed 's/,$//')
            printf "  ${YELLOW}%-25s${NC} %d skills: %s\n" "$bundle_name" "$count" "$skill_names"
        done <<<"$(bundle_list)" | sort
        ;;

    persona)
        echo -e "${BOLD}Installing persona: $TARGET${NC}"
        mkdir -p "$SKILLS_DIR"
        skill_path=$(find_skill "$TARGET" "personas")
        if [ -n "$skill_path" ]; then
            install_skill "$skill_path"
        else
            echo -e "  ${RED}✗${NC} Persona '$TARGET' not found"
            echo "  Run --list to see available personas"
            exit 1
        fi
        ;;

    agent)
        echo -e "${BOLD}Installing agent: $TARGET${NC}"
        mkdir -p "$SKILLS_DIR"
        skill_path=$(find_skill "$TARGET" "agents")
        if [ -n "$skill_path" ]; then
            install_skill "$skill_path"
        else
            echo -e "  ${RED}✗${NC} Agent '$TARGET' not found"
            echo "  Run --list to see available agents"
            exit 1
        fi
        ;;

    workflow)
        echo -e "${BOLD}Installing workflow: $TARGET${NC}"
        mkdir -p "$SKILLS_DIR"
        skill_path=$(find_skill "$TARGET" "workflows")
        if [ -n "$skill_path" ]; then
            install_skill "$skill_path"
        else
            echo -e "  ${RED}✗${NC} Workflow '$TARGET' not found"
            echo "  Run --list to see available workflows"
            exit 1
        fi
        ;;

    bundle)
        if ! bundle_exists "$TARGET"; then
            echo -e "${RED}Unknown bundle: $TARGET${NC}"
            echo "Available bundles:"
            bundle_list | sed 's/^/  /'
            exit 1
        fi

        if $PREVIEW; then
            echo -e "${BOLD}Previewing bundle: $TARGET${NC}"
            bundle_preview "$TARGET"
            exit 0
        fi

        echo -e "${BOLD}Installing bundle: $TARGET${NC}"
        mkdir -p "$SKILLS_DIR"

        skills="$(bundle_skills "$TARGET")"
        if [ -z "$skills" ]; then
            echo -e "  ${RED}✗${NC} Bundle '$TARGET' has no skills defined"
            exit 1
        fi

        for skill_path in $skills; do
            install_skill "$skill_path"
        done

        hooks="$(bundle_hooks "$TARGET")"
        if [ -n "$hooks" ]; then
            echo ""
            echo -e "${YELLOW}Hooks referenced (not auto-installed):${NC}"
            for hook in $hooks; do
                echo "  - $hook"
            done
        fi

        echo ""
        if $DRY_RUN; then
            echo -e "${BLUE}Dry run complete — no files were modified${NC}"
        else
            write_manifest "$TARGET" "$skills" "$hooks"
            echo -e "${GREEN}Bundle '$TARGET' installed to $SKILLS_DIR${NC}"
        fi
        ;;

    hooks)
        echo -e "${BOLD}Installing hooks${NC}"
        install_hooks
        echo ""
        echo -e "${GREEN}Hooks installed to $HOOKS_DIR${NC}"
        echo "Configure in .claude/settings.json — see hooks/README.md for details"
        ;;

    all)
        echo -e "${BOLD}Installing all skills${NC}"
        mkdir -p "$SKILLS_DIR"
        echo ""

        echo -e "${BLUE}Personas:${NC}"
        while IFS= read -r -d '' skill_md; do
            dir="$(dirname "$skill_md")"
            rel_dir="${dir#$REPO_ROOT/}"
            install_skill "$rel_dir"
        done < <(find "$REPO_ROOT/personas" -name "SKILL.md" -print0 2>/dev/null | sort -z)

        echo ""
        echo -e "${BLUE}Agents:${NC}"
        while IFS= read -r -d '' skill_md; do
            dir="$(dirname "$skill_md")"
            rel_dir="${dir#$REPO_ROOT/}"
            install_skill "$rel_dir"
        done < <(find "$REPO_ROOT/agents" -name "SKILL.md" -print0 2>/dev/null | sort -z)

        echo ""
        echo -e "${BLUE}Workflows:${NC}"
        while IFS= read -r -d '' skill_md; do
            dir="$(dirname "$skill_md")"
            rel_dir="${dir#$REPO_ROOT/}"
            install_skill "$rel_dir"
        done < <(find "$REPO_ROOT/workflows" -name "SKILL.md" -print0 2>/dev/null | sort -z)

        echo ""
        echo -e "${BLUE}Hooks:${NC}"
        install_hooks

        echo ""
        echo -e "${GREEN}All skills installed to $SKILLS_DIR${NC}"
        ;;

    uninstall)
        if [ -n "$TARGET" ]; then
            uninstall_bundle "$TARGET"
        else
            echo -e "${BOLD}Removing all installed skills${NC}"
            if [ -d "$SKILLS_DIR" ]; then
                count=$(find "$SKILLS_DIR" -maxdepth 1 -mindepth 1 | wc -l)
                rm -rf "${SKILLS_DIR:?}"/*
                echo -e "  ${GREEN}✓${NC} Removed $count skills from $SKILLS_DIR"
            else
                echo "  Nothing to remove — $SKILLS_DIR does not exist"
            fi
        fi
        ;;
esac

echo ""
echo "Done."
