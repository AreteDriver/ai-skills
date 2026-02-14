#!/usr/bin/env bash
# install.sh — Install ai-skills personas, agents, hooks, and bundles.
# Usage:
#   ./tools/install.sh --all                    Install everything
#   ./tools/install.sh --persona code-reviewer  Install one persona
#   ./tools/install.sh --bundle webapp-security Install a curated bundle
#   ./tools/install.sh --list                   List available skills and bundles
#   ./tools/install.sh --uninstall              Remove installed skills
#
# Installs to ~/.claude/skills/ by default (override with CLAUDE_SKILLS_DIR).

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SKILLS_DIR="${CLAUDE_SKILLS_DIR:-$HOME/.claude/skills}"
HOOKS_DIR="${CLAUDE_HOOKS_DIR:-$HOME/.claude/hooks}"
SYMLINK=false
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
    --all                       Install all personas + hooks
    --persona <name>            Install a single persona skill
    --agent <name>              Install a single agent skill
    --bundle <name>             Install a curated bundle
    --hooks                     Install all hook scripts
    --list                      List available skills and bundles
    --uninstall                 Remove all installed skills

OPTIONS:
    --symlink                   Symlink instead of copy (for development)
    --dir <path>                Override install directory (default: ~/.claude/skills)
    --help                      Show this help

BUNDLES:
    webapp-security             code-reviewer + security-auditor + testing-specialist
    release-engineering         release-engineer + code-reviewer + cicd-pipeline
    data-pipeline               data-engineer + data-analyst + data-visualizer + report-generator
    full-stack-dev              senior-software-engineer + code-reviewer + testing-specialist + software-architect
    claude-code-dev             hooks-designer + plugin-builder + mcp-server-builder + cicd-pipeline

EXAMPLES:
    ./tools/install.sh --list
    ./tools/install.sh --bundle webapp-security
    ./tools/install.sh --persona code-reviewer --symlink
    ./tools/install.sh --all
EOF
    exit 0
}

# ─────────────────────────────────────────────
# Bundle definitions
# ─────────────────────────────────────────────
declare -A BUNDLES
BUNDLES[webapp-security]="personas/engineering/code-reviewer personas/security/security-auditor personas/engineering/testing-specialist personas/security/accessibility-checker"
BUNDLES[release-engineering]="personas/engineering/code-reviewer personas/claude-code/cicd-pipeline"
BUNDLES[data-pipeline]="personas/data/data-engineer personas/data/data-analyst personas/data/data-visualizer personas/data/report-generator"
BUNDLES[full-stack-dev]="personas/engineering/senior-software-engineer personas/engineering/code-reviewer personas/engineering/testing-specialist personas/engineering/software-architect personas/engineering/documentation-writer"
BUNDLES[claude-code-dev]="personas/claude-code/hooks-designer personas/claude-code/plugin-builder personas/claude-code/mcp-server-builder personas/claude-code/cicd-pipeline personas/claude-code/session-memory-manager"

# ─────────────────────────────────────────────
# Parse arguments
# ─────────────────────────────────────────────
while [[ $# -gt 0 ]]; do
    case $1 in
        --all)       ACTION="all"; shift ;;
        --persona)   ACTION="persona"; TARGET="$2"; shift 2 ;;
        --agent)     ACTION="agent"; TARGET="$2"; shift 2 ;;
        --bundle)    ACTION="bundle"; TARGET="$2"; shift 2 ;;
        --hooks)     ACTION="hooks"; shift ;;
        --list)      ACTION="list"; shift ;;
        --uninstall) ACTION="uninstall"; shift ;;
        --symlink)   SYMLINK=true; shift ;;
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
    local type="$2"  # personas or agents

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

# ─────────────────────────────────────────────
# Actions
# ─────────────────────────────────────────────
case $ACTION in
    list)
        echo -e "${BOLD}Available Personas:${NC}"
        for base_dir in personas/engineering personas/data personas/devops personas/claude-code personas/security personas/domain; do
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
        echo -e "${BOLD}Available Bundles:${NC}"
        for bundle_name in "${!BUNDLES[@]}"; do
            skills="${BUNDLES[$bundle_name]}"
            count=$(echo "$skills" | wc -w)
            skill_names=$(echo "$skills" | tr ' ' '\n' | xargs -I{} basename {} | tr '\n' ', ' | sed 's/,$//')
            printf "  ${YELLOW}%-25s${NC} %d skills: %s\n" "$bundle_name" "$count" "$skill_names"
        done | sort
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

    bundle)
        if [ -z "${BUNDLES[$TARGET]+_}" ]; then
            echo -e "${RED}Unknown bundle: $TARGET${NC}"
            echo "Available bundles: ${!BUNDLES[*]}"
            exit 1
        fi

        echo -e "${BOLD}Installing bundle: $TARGET${NC}"
        mkdir -p "$SKILLS_DIR"

        for skill_path in ${BUNDLES[$TARGET]}; do
            install_skill "$skill_path"
        done

        echo ""
        echo -e "${GREEN}Bundle '$TARGET' installed to $SKILLS_DIR${NC}"
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
        echo -e "${BLUE}Hooks:${NC}"
        install_hooks

        echo ""
        echo -e "${GREEN}All skills installed to $SKILLS_DIR${NC}"
        ;;

    uninstall)
        echo -e "${BOLD}Removing installed skills${NC}"
        if [ -d "$SKILLS_DIR" ]; then
            count=$(find "$SKILLS_DIR" -maxdepth 1 -mindepth 1 | wc -l)
            rm -rf "${SKILLS_DIR:?}"/*
            echo -e "  ${GREEN}✓${NC} Removed $count skills from $SKILLS_DIR"
        else
            echo "  Nothing to remove — $SKILLS_DIR does not exist"
        fi
        ;;
esac

echo ""
echo "Done."
