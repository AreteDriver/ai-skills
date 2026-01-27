# Development Prompt Collection

Battle-tested prompt patterns for common development workflows.

---

## GitHub Profile Optimization

```
Analyze my GitHub profile (username: [USERNAME]) and suggest improvements for:
1. Bio and description — make it compelling for recruiters and collaborators
2. Pinned repositories — which repos showcase my skills best
3. README profile — structure and content recommendations
4. Contribution graph — strategies for consistent activity
5. Repository descriptions and topics — SEO and discoverability
```

---

## CI/CD Diagnostics

```
My CI/CD pipeline is failing. Here's the context:
- Platform: [GitHub Actions / GitLab CI / Jenkins / etc.]
- Error log: [paste relevant logs]
- Recent changes: [what changed before it broke]
- Pipeline file: [paste config]

Diagnose the failure. Identify root cause, suggest a fix, and recommend
preventive measures so this class of failure doesn't recur.
```

---

## Project Scaffolding

```
Scaffold a new project with these requirements:
- Language/Framework: [e.g., TypeScript + Express]
- Purpose: [what the project does]
- Features needed: [list core features]
- Deployment target: [e.g., Docker, AWS Lambda, Vercel]

Include:
- Directory structure
- Package configuration
- Linting and formatting setup
- Basic CI pipeline
- README template
- .gitignore appropriate for the stack
```

---

## Code Review Request

```
Review this code for:
1. Correctness — bugs, logic errors, edge cases
2. Security — injection, auth issues, data exposure
3. Performance — unnecessary work, N+1 queries, memory leaks
4. Maintainability — naming, structure, complexity
5. Testing — what tests are missing

Categorize findings as: critical / suggestion / nit
```

---

## Debug Session

```
I'm debugging an issue:
- Expected behavior: [what should happen]
- Actual behavior: [what's happening instead]
- Steps to reproduce: [how to trigger the bug]
- Environment: [OS, runtime version, relevant config]
- What I've already tried: [list attempts]

Help me systematically narrow down the root cause.
```

---

## Architecture Decision

```
I need to make an architecture decision:
- Context: [what system/feature this is for]
- Options I'm considering: [list options]
- Constraints: [team size, timeline, budget, existing tech]
- Quality attributes that matter most: [scalability, simplicity, speed, etc.]

Present each option with trade-offs and give a recommendation with rationale.
```

---

## Universal Prompt Template

```
Context: [Background information and current situation]
Task: [Specific action or output needed]
Constraints: [Limitations, requirements, or boundaries]
Format: [Desired output structure]
Examples: [Optional — sample input/output for clarity]
```
