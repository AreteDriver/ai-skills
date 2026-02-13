---
name: intent-author
description: Teaches agents how to publish well-structured intents for Convergent's intent graph. Defines the schema, quality criteria, and authoring patterns for intent nodes. Without this skill, agents publish vague or malformed intents and convergence fails. Use whenever an agent needs to declare what it's building, what it provides, what it requires, and what constraints it imposes within a Convergent-coordinated workflow.
---

# Intent Author

Convergent's intent graph only works if agents publish intents that are
specific, machine-comparable, and honest about uncertainty. This skill
teaches agents how to author good intents.

## Why This Exists

The intent graph is Convergent's core data structure. Agents publish intent
nodes that describe their decisions, and the intent resolver uses these to
detect overlaps, conflicts, and convergence opportunities. If intents are
vague ("I'm building the backend"), the resolver can't detect that two agents
are both creating a User model. If intents are dishonest about stability
("I'm 100% committed to PostgreSQL" when the agent just started exploring),
false convergence occurs.

Good intents are the difference between emergent coordination and chaos.

## When to Activate

- Before any agent publishes to the intent graph
- When an agent's work reaches a decision point (choosing a data model, API shape, dependency)
- When updating an existing intent (stability changed, scope refined)
- During intent review ("are my intents well-formed?")

## Intent Node Schema

Every intent published to the graph must include:

```python
@dataclass
class IntentNode:
    # ─── Identity ───
    id: str                     # Unique ID (auto-generated)
    agent_id: str               # Which agent published this
    timestamp: str              # When published (ISO 8601)

    # ─── What ───
    action: str                 # What the agent is doing
                                # MUST be specific and verifiable
                                # Good: "Creating User model with email, name, role fields"
                                # Bad:  "Working on authentication"

    category: str               # decision | interface | dependency | constraint
                                # decision: an architectural choice
                                # interface: a public API or data shape
                                # dependency: something this agent needs from elsewhere
                                # constraint: a rule other agents must respect

    # ─── Contracts ───
    provides: list[str]         # What this intent makes available to others
                                # Good: ["User model", "AuthService.authenticate() method"]
                                # Bad:  ["auth stuff"]

    requires: list[str]         # What this intent needs from others
                                # Good: ["Database connection", "email validation library"]
                                # Bad:  ["some dependencies"]

    constraints: list[str]      # Rules this intent imposes
                                # Good: ["User.email must be unique", "passwords bcrypt-hashed"]
                                # Bad:  ["should be secure"]

    # ─── Confidence ───
    stability: float            # 0.0 (just exploring) to 1.0 (committed, tested, deployed)
    evidence: list[str]         # What supports this stability score
                                # Good: ["tests pass", "3 dependents adopted this interface"]
                                # Bad:  [] (empty — no evidence for claimed stability)

    # ─── Scope ───
    files_affected: list[str]   # Which files this intent touches
    interfaces_affected: list[str]  # Which APIs/schemas this changes
```

## Stability Scoring Guide

Stability is the most important field. It determines whether other agents
adopt this intent or treat it as tentative.

| Score | Meaning | Evidence Required |
|-------|---------|-------------------|
| 0.0-0.2 | **Exploring** — considering options, nothing committed | None needed |
| 0.3-0.4 | **Drafting** — initial implementation started | File created, basic structure |
| 0.5-0.6 | **Implementing** — substantial code written | Functions defined, logic present |
| 0.7-0.8 | **Testing** — code works, tests written | Tests pass |
| 0.9 | **Committed** — other agents depend on this | Dependents exist, interface stable |
| 1.0 | **Locked** — changing this would break things | In production, multiple dependents |

**Rules:**
- Never claim stability > 0.6 without passing tests
- Never claim stability > 0.8 without at least one dependent
- Stability can decrease (you discovered a problem) — publish an update
- Empty evidence array with stability > 0.3 is invalid

## Authoring Patterns

### Pattern 1: Interface Declaration

When your agent creates something other agents will consume:

```python
IntentNode(
    action="Defining User model for authentication module",
    category="interface",
    provides=["User model with fields: id (int), email (str), name (str), role (enum)"],
    requires=["SQLite database connection via get_db() context manager"],
    constraints=[
        "User.email must be unique (UNIQUE constraint)",
        "User.role must be one of: admin, analyst, viewer",
        "User.id is auto-incremented, never set manually"
    ],
    stability=0.7,
    evidence=["User model defined in models.py", "3 tests pass for CRUD operations"],
    files_affected=["src/models.py", "src/db/schema.sql"],
    interfaces_affected=["User table schema", "UserCreate/UserResponse Pydantic models"]
)
```

### Pattern 2: Dependency Declaration

When your agent needs something from another agent:

```python
IntentNode(
    action="MealPlanService needs Recipe model to build meal plans",
    category="dependency",
    provides=["MealPlan model referencing Recipe via foreign key"],
    requires=[
        "Recipe model with fields: id, title, ingredients, prep_time",
        "Recipe.id must be stable (used as FK in MealPlan)"
    ],
    constraints=[],
    stability=0.4,  # Still drafting — waiting for Recipe to stabilize
    evidence=["MealPlanService skeleton created"],
    files_affected=["src/meal_plans/models.py", "src/meal_plans/service.py"],
    interfaces_affected=["MealPlan table schema"]
)
```

### Pattern 3: Constraint Declaration

When your agent makes a decision that constrains others:

```python
IntentNode(
    action="All API endpoints must use JWT authentication",
    category="constraint",
    provides=["auth_required() decorator for FastAPI routes"],
    requires=["JWT secret key in environment variables"],
    constraints=[
        "All /api/* routes must use auth_required() decorator",
        "JWT tokens expire after 24 hours",
        "Refresh tokens are NOT implemented in v1"
    ],
    stability=0.8,
    evidence=["auth middleware tested", "3 routes using decorator"],
    files_affected=["src/auth/middleware.py", "src/auth/jwt.py"],
    interfaces_affected=["All API route signatures"]
)
```

### Pattern 4: Decision Declaration

When your agent makes an architectural choice:

```python
IntentNode(
    action="Using SQLite instead of PostgreSQL for data storage",
    category="decision",
    provides=["SQLite database at data/app.db"],
    requires=[],
    constraints=[
        "Single-writer limitation — no concurrent write transactions",
        "WAL mode enabled for read concurrency",
        "Maximum database size ~1GB for this use case"
    ],
    stability=0.9,
    evidence=[
        "Database schema created and migrated",
        "5 modules depend on SQLite connection",
        "Performance tested with 10K documents"
    ],
    files_affected=["src/db/database.py", "src/db/schema.sql"],
    interfaces_affected=["get_db() context manager", "All SQL queries"]
)
```

## Anti-Patterns (What NOT to Do)

### Vague Intent
```python
# BAD
IntentNode(
    action="Working on the backend",
    provides=["backend stuff"],
    requires=["some libraries"],
    stability=0.5,
    evidence=[]  # No evidence!
)
```
**Why bad:** No other agent can determine overlap or conflict. "Backend stuff"
is not machine-comparable.

### Overconfident Stability
```python
# BAD
IntentNode(
    action="User authentication system",
    stability=0.9,  # Claims near-committed
    evidence=["started writing code"]  # But barely started
)
```
**Why bad:** Other agents will adopt this as stable, then face breaking changes.

### Missing Constraints
```python
# BAD
IntentNode(
    action="Creating REST API for user management",
    provides=["POST /users, GET /users/:id, PUT /users/:id"],
    constraints=[]  # No constraints declared
)
```
**Why bad:** Another agent might create conflicting routes or assume different
auth requirements. Always declare constraints, even if they seem obvious.

### Stale Intent
```python
# BAD — intent published 2 hours ago, code has changed significantly since
# Agent forgot to update the intent graph
```
**Why bad:** Other agents are making decisions based on outdated information.
**Rule:** Update your intent whenever stability changes by ±0.2 or scope changes.

## Quality Checklist

Before publishing any intent, verify:

- [ ] `action` is specific enough that another agent could verify it
- [ ] `provides` lists concrete artifacts, not vague descriptions
- [ ] `requires` is complete — nothing silently assumed
- [ ] `constraints` includes anything that would surprise another agent
- [ ] `stability` is honest and supported by `evidence`
- [ ] `evidence` is non-empty for stability > 0.3
- [ ] `files_affected` is accurate (not stale)
- [ ] No overlap with an existing intent you should consume instead

## Integration with Convergent

This skill is consumed by Convergent's `IntentResolver`:

```python
class IntentResolver:
    def __init__(self, intent_author_skill):
        self.skill = intent_author_skill

    def validate_intent(self, intent: IntentNode) -> list[str]:
        """Validate intent quality before publishing to graph."""
        issues = []

        if len(intent.action) < 20:
            issues.append("Action too vague — be more specific")

        if intent.stability > 0.3 and not intent.evidence:
            issues.append("Stability > 0.3 requires evidence")

        if intent.stability > 0.6 and "test" not in " ".join(intent.evidence).lower():
            issues.append("Stability > 0.6 should have test evidence")

        if intent.category == "interface" and not intent.provides:
            issues.append("Interface intent must declare what it provides")

        if intent.category == "constraint" and not intent.constraints:
            issues.append("Constraint intent must declare constraints")

        return issues
```

## Constraints

- **Validation before publishing** — every intent runs through quality checklist
- **Honest stability** — penalize agents that consistently overstate stability
- **Update or retract** — stale intents (>1 hour without update during active work) should be flagged
- **No circular dependencies** — intent A requires intent B requires intent A is invalid
- **Provenance tracked** — every intent records which agent, when, and what evidence
