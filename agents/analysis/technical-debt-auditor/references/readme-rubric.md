# README Quality Rubric

Checklist for scoring README documentation. Each item is worth points toward
the Documentation category score.

## Essential (0-4 points without these)

- [ ] **Project name** — clearly stated at top
- [ ] **One-line description** — what this project does (not just what it is)
- [ ] **Installation steps** — copy-pasteable commands that work
- [ ] **Quick start / usage example** — how to actually use it after installing

## Standard (5-7 range)

- [ ] **What problem it solves** — why someone would use this
- [ ] **Prerequisites** — Python version, system deps, API keys needed
- [ ] **Configuration** — environment variables, config files
- [ ] **License** — stated in README or LICENSE file present

## Professional (8-9 range)

- [ ] **API reference** — or link to generated docs
- [ ] **Architecture overview** — for complex projects (diagram or text)
- [ ] **Examples** — multiple use cases, not just hello world
- [ ] **Contributing guidelines** — how to submit PRs, code style

## Showcase (10)

- [ ] **Screenshots/demo** — visual proof it works (for UI projects)
- [ ] **Badges** — CI status, coverage, version, license
- [ ] **CHANGELOG** — maintained version history
- [ ] **Troubleshooting / FAQ** — common issues addressed
- [ ] **Comparison** — how this differs from alternatives

## Anti-Patterns (Score Deductions)

- README is auto-generated boilerplate (GitHub template untouched): -3
- README references features that don't exist: -2
- Install steps don't actually work: -2
- README is a single line: score capped at 1
- No README at all: score = 0
