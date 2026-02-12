# Quickstart: AI Skills in 90 Seconds

This guide shows how skills transform Claude from a generic assistant into a specialized expert. Pick a skill, load it, and see the difference.

## Setup

```bash
# Clone the repo
git clone https://github.com/AreteDriver/ai_skills.git
cd ai_skills

# Validate everything works
./tools/validate-skills.sh
```

## Try It: Code Review Skill

### 1. Copy the skill into your project

```bash
# Option A: Copy directly
cp -r personas/engineering/code-reviewer ~/.claude/skills/

# Option B: Reference in your project's CLAUDE.md
echo "See skills from: $(pwd)/personas/engineering/code-reviewer/SKILL.md" >> ~/my-project/CLAUDE.md
```

### 2. See the difference

Ask Claude to review this function:

```python
def process_user(data):
    query = f"SELECT * FROM users WHERE id = {data['id']}"
    result = db.execute(query)
    return {"password": result.password, "ssn": result.ssn, "name": result.name}
```

**Without the skill** (generic Claude):

> This function takes user data, queries the database, and returns user information.
> You might want to add some error handling.

**With the code-reviewer skill** (structured, severity-ranked, actionable):

> ## Code Review Summary
>
> ### Overview
> Critical security vulnerabilities in user data handling. Must fix before merge.
>
> ### Critical Issues
> - **process_user:2** SQL injection via string interpolation
>   - Impact: Attacker can read/modify/delete entire database
>   - Fix: Use parameterized queries: `db.execute("SELECT * FROM users WHERE id = ?", [data['id']])`
>
> - **process_user:3** Sensitive data exposure in response
>   - Impact: Password hashes and SSNs returned to client
>   - Fix: Return only necessary fields: `{"name": result.name}`
>
> ### Suggestions
> - **process_user:1** Add input validation for `data['id']`
>   - Recommendation: Validate type and range before query
>
> ### Security Considerations
> - No authentication check before data access
> - No rate limiting on user lookups
>
> ### What's Good
> - Function has a clear single responsibility

The skill gives Claude a **review framework**: severity categories, line references, impact analysis, and concrete fixes—instead of vague suggestions.

---

## Try It: Senior Software Engineer Skill

### 1. Load the skill

```bash
cp -r personas/engineering/senior-software-engineer ~/.claude/skills/
```

### 2. See the difference

Ask Claude: *"Should I use microservices for my new side project?"*

**Without the skill:**

> Microservices offer scalability and independent deployment. Here are some
> pros and cons to consider...

**With the senior-software-engineer skill** (opinionated, experience-driven):

> No. A side project should start as a monolith. Here's why:
>
> **The problem with microservices here:**
> - You don't have the traffic patterns to justify distributed systems overhead
> - Service boundaries are unknown until you understand your domain
> - You're trading development speed for operational complexity you don't need yet
>
> **What I'd recommend:**
> 1. Start monolithic with clear module boundaries
> 2. Use interfaces between modules so extraction is possible later
> 3. Split only when you have concrete scaling evidence (not hypothetical)
>
> The "never" list applies here: don't add unnecessary abstractions or
> premature optimization. A well-structured monolith beats a poorly-bounded
> microservice mesh every time.

The skill gives Claude an **engineering perspective**: direct answers backed by trade-off analysis, not just a balanced list of pros and cons.

---

## Try It: Feature Implementation Workflow

### 1. Load the workflow

```bash
cp -r workflows/feature-implementation ~/.claude/skills/
```

### 2. See the difference

Ask Claude: *"Add user authentication to my Express app"*

**Without the workflow:**

> Here's how to add authentication:
> ```js
> app.post('/login', (req, res) => { ... })
> ```

**With the feature-implementation workflow** (structured phases, WHY/WHAT/HOW):

> ## Phase 1: Requirements (WHY)
> - **Goal:** Prevent unauthorized access to protected routes
> - **Success criteria:** Users can register, login, access protected routes; unauthorized requests return 401
> - **Anti-goals:** Not building OAuth/social login, not building admin roles (yet)
>
> ## Phase 2: Design (WHAT)
> - **Files to create:** `src/middleware/auth.js`, `src/routes/auth.js`, `src/models/user.js`
> - **Files to modify:** `src/app.js` (mount auth routes), `package.json` (add bcrypt, jsonwebtoken)
> - **Dependencies:** bcrypt, jsonwebtoken
>
> ## Phase 3: Implementation (HOW)
> - **Step 1:** Create User model with hashed password storage
> - **Step 2:** Build register/login endpoints
> - **Step 3:** Create JWT middleware for protected routes
> - **Step 4:** Add middleware to existing routes
> - **Quality gate:** All auth tests pass, no plaintext passwords in DB
>
> Shall I proceed with Phase 3?

The workflow forces Claude to **capture intent and scope before writing code**—preventing the most common failure mode: building the wrong thing.

---

## What's Next

| Want to... | Do this |
|------------|---------|
| Browse all 46 skills | See [registry.yaml](../../registry.yaml) |
| Create your own skill | Copy [templates/skill-template.md](../../templates/skill-template.md) |
| Add hooks to your workflow | See [hooks/README.md](../../hooks/README.md) |
| Run the full feature workflow | See [playbooks/full-feature.md](../../playbooks/full-feature.md) |
| Validate your skills | Run `./tools/validate-skills.sh` |
