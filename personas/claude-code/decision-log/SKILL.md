---
name: decision-log
description: Log high-leverage decisions from the current work session to the Arete Decision Log. Extracts architecture, UX, scope, tooling, and philosophy decisions. Invoke with /decision-log or /adl.
---

# Decision Log Skill

Log high-leverage decisions from the current work session.

## Process

1. **Scan conversation** for decisions that:
   - Remove options or lock architecture
   - Choose between alternatives
   - Set scope boundaries
   - Select tooling/frameworks
   - Establish principles

2. **Generate ADL entry** for each:
   ```markdown
   ## ADL-YYYYMMDD-###
   **Project:** [from context]
   **Decision Class:** [ARCH|UX|SCOPE|TOOLING|PHIL]

   **Decision:** [one sentence]

   **Chosen Option:** [selected approach]

   **Rejected Options:**
   - [alternative 1]
   - [alternative 2]

   **Why:**
   - [reason 1]
   - [reason 2]

   **Tradeoffs Accepted:**
   - [what was given up]

   **Revisit If:**
   - [invalidation condition]
   ```

3. **Route by Project visibility** (see Routing Rule below), then append to the chosen file. Before writing, two precheck commands:
   - `grep '^## ADL-YYYYMMDD-' <chosen-file>` to find today's highest sequence **for that file** and increment — sequence is **per-day per-file**, not shared across the two logs.
   - **Format-match check** (mandatory): `grep -A1 '^## ADL-' <chosen-file> | head -6` to confirm existing entries use the same field syntax (`**Project**:` vs `**Project:**` — both are seen in the wild; match what the file already uses). If the target file has zero ADL-shaped entries, STOP and surface to user: the path may have drifted.

4. **Report** what was logged, including which log it landed in and why.

## Routing Rule

ARETE keeps two parallel decision logs by visibility. Route each ADL by the Project field:

| Log | Path | Use for | Project examples |
|---|---|---|---|
| **Public** | `~/projects/notes/decisions/YYYY-MM.md` (in public repo `AreteDriver/notes`) | Open-source projects, identity/philosophy decisions, engineering practice, anything publishable on Substack or discussable in interviews | `arete-evals`, `BenchGoblins`, `anchormd` (post-launch), `tiaid`, `ai-skills`, `Portfolio / Job hunt positioning`, identity decisions like "engineer not researcher" |
| **Private** | `~/projects/DecisionLog/DECISIONS.md` (in private repo `AreteDriver/DecisionLog`) | Strategic build choices, product monetization positioning, pre-launch product decisions, internal tooling, anything competitively sensitive | `Animus` (build path), `memboot` (pricing/launch), `WatchTower`, `Dossier`, `Argus`, `Gorgon`, `Aurora-Arcology`, `Crucible` research, internal tools |

**When the Project is unclear or ambiguous**: surface the routing question to the user before writing. State the candidates and ask. **Default to PRIVATE on ambiguity** — easier to promote a private entry to public than to retract a public one.

**Cross-check**: when in doubt, look at how the same Project's recent ADLs were routed. The user's existing pattern is usually the answer.

**Do NOT cross-write** the same ADL to both files. Sequence numbers are per-file-per-day; writing to both creates a fake conflict where ADL-YYYYMMDD-001 means different things in different files (already happened today before this rule was codified — see ADL-20260523-001 in each file for the divergent example).

## Decision Classes

| Class | Use For |
|-------|---------|
| ARCH | System design, APIs, data models |
| UX | Controls, interactions, experience |
| SCOPE | Feature cuts, MVP boundaries |
| TOOLING | Languages, frameworks, build |
| PHIL | Strategy, principles, values |

## Detection Patterns

Look for:
- "chose X over Y"
- "decided to"
- "went with"
- "cut/dropped/excluded"
- Options presented then one selected
- Architecture discussions

## What NOT to Log

- Reversible in minutes
- Implementation details
- Bug fixes
- Routine changes
