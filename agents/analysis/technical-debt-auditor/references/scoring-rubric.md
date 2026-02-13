# Scoring Rubric — Technical Debt Auditor

Each category is scored 0-10. This rubric defines what each score means so results
are consistent across repos and over time.

---

## 1. Security (Critical — Blocker)

**If ANY critical finding exists, overall health score is capped at 3.0.**

| Score | Criteria |
|-------|----------|
| 10 | No secrets in code or git history. All deps pass vulnerability scan. .env in .gitignore. No hardcoded credentials. |
| 8-9 | No critical vulnerabilities. 1-2 low-severity dep advisories. Proper .gitignore. |
| 6-7 | No secrets exposed, but some medium-severity dep vulnerabilities unpatched. |
| 4-5 | .env committed but contains only non-sensitive config. Or 1+ high-severity dep vulnerability. |
| 2-3 | API keys or tokens found in code (even if revoked). Or critical dep vulnerability present. |
| 0-1 | Active secrets committed. Credentials in git history. Critical CVEs in dependencies. |

### What to scan
```bash
# Secrets (grep patterns)
grep -rn --include="*.py" --include="*.js" --include="*.ts" --include="*.env" \
  -E "(api_key|API_KEY|secret|SECRET|password|PASSWORD|token|TOKEN)\s*[=:]\s*['\"][^'\"]+['\"]" .

# Git history secrets
git log --all -p | grep -iE "(api_key|secret|password|token)\s*[=:]" | head -20

# .env in git
git ls-files | grep -i "\.env"

# Dependency vulnerabilities
pip-audit 2>/dev/null          # Python
npm audit 2>/dev/null          # Node
cargo audit 2>/dev/null        # Rust
```

---

## 2. Correctness (High Weight)

| Score | Criteria |
|-------|----------|
| 10 | Tests exist, all pass, coverage >80%, edge cases covered, integration tests present. |
| 8-9 | Tests exist, all pass, coverage >60%. Some edge cases missing. |
| 6-7 | Tests exist, mostly pass (1-2 failures). Coverage >40%. |
| 4-5 | Tests exist but many fail. Or tests exist but coverage <20%. |
| 2-3 | Test files exist but are empty/broken. Or only 1-2 trivial tests. |
| 0-1 | No tests at all. No test directory. No test configuration. |

### What to scan
```bash
# Test discovery
find . -name "test_*.py" -o -name "*_test.py" -o -name "*.test.js" -o -name "*.spec.ts" | wc -l

# Test runner detection
ls pytest.ini setup.cfg pyproject.toml .pytest_cache 2>/dev/null  # Python
ls jest.config.* vitest.config.* 2>/dev/null                      # Node
ls Cargo.toml 2>/dev/null && grep "\[dev-dependencies\]" Cargo.toml  # Rust

# Run tests (sandboxed)
pytest --tb=short -q 2>&1
npm test 2>&1
cargo test 2>&1

# Coverage (if configured)
pytest --cov --cov-report=term-missing 2>&1
```

---

## 3. Infrastructure (High Weight — 2x Career)

| Score | Criteria |
|-------|----------|
| 10 | CI/CD passes. Dockerfile works. Install from scratch succeeds. Reproducible build. Makefile or equivalent. |
| 8-9 | CI/CD exists and passes. Install works. Missing Docker or missing Makefile. |
| 6-7 | CI/CD exists but has failures. Or install works but requires undocumented steps. |
| 4-5 | No CI/CD. Install works if you know the right incantation. Dockerfile exists but is broken. |
| 2-3 | Install fails. No CI. No Docker. Requirements file exists but is incomplete. |
| 0-1 | No requirements file. No install instructions. No CI. Project cannot be built by a stranger. |

### What to scan
```bash
# CI/CD detection
ls .github/workflows/*.yml .gitlab-ci.yml Jenkinsfile .circleci/config.yml 2>/dev/null

# Dockerfile
ls Dockerfile docker-compose.yml 2>/dev/null

# Build system
ls Makefile justfile Taskfile.yml 2>/dev/null

# Requirements completeness
pip install -r requirements.txt 2>&1  # Python (sandboxed)
npm install 2>&1                       # Node (sandboxed)
cargo build 2>&1                       # Rust (sandboxed)

# Entry point verification
python -m <package> --help 2>&1
npm start 2>&1
cargo run -- --help 2>&1
```

---

## 4. Maintainability (Medium Weight)

| Score | Criteria |
|-------|----------|
| 10 | Clean module structure. Consistent naming. No TODOs. No dead code. Type hints (Python) or TypeScript. Linter configured and passing. |
| 8-9 | Good structure. <5 TODOs. Minor naming inconsistencies. Linter configured. |
| 6-7 | Reasonable structure. 5-15 TODOs. Some long functions (>100 lines). No linter. |
| 4-5 | Flat structure (everything in 1-2 files). 15-30 TODOs. God functions. |
| 2-3 | Spaghetti code. 30+ TODOs. Circular imports. Copy-pasted blocks. |
| 0-1 | Unreadable. No structure. Commented-out code everywhere. |

### What to scan
```bash
# TODO/FIXME count
grep -rn --include="*.py" --include="*.js" --include="*.ts" "TODO\|FIXME\|HACK\|XXX" . | wc -l

# Dead code indicators (Python)
find . -name "*.py" -exec grep -l "^# .*def \|^#.*class " {} \;

# File size outliers (likely god files)
find . -name "*.py" -o -name "*.js" -o -name "*.ts" | xargs wc -l 2>/dev/null | sort -rn | head -10

# Module depth
find . -name "*.py" -not -path "*/venv/*" -not -path "*/__pycache__/*" | head -30

# Linter config
ls .flake8 .pylintrc .eslintrc* ruff.toml pyproject.toml 2>/dev/null | xargs grep -l "ruff\|flake8\|pylint\|eslint" 2>/dev/null

# Type hints (Python) — rough check
grep -rn "def .*(.*):" --include="*.py" | head -20 | grep -c "->"
```

---

## 5. Documentation (Medium Weight — 2x Career)

| Score | Criteria |
|-------|----------|
| 10 | Comprehensive README (purpose, install, usage, examples, API, architecture, contributing, license). Docstrings on public functions. CHANGELOG maintained. |
| 8-9 | Good README with install + usage + examples. Most public functions documented. LICENSE present. |
| 6-7 | README exists with basic description and install. Some docstrings. LICENSE present. |
| 4-5 | README exists but is boilerplate or outdated. Few docstrings. |
| 2-3 | README is a single line or auto-generated. No docstrings. |
| 0-1 | No README. No documentation at all. |

### README Quality Checklist (see references/readme-rubric.md)

```
[ ] Project name and one-line description
[ ] What problem it solves (not just what it is)
[ ] Installation steps (copy-pasteable)
[ ] Quick start / usage example
[ ] API reference or link to docs
[ ] Architecture overview (for complex projects)
[ ] Contributing guidelines
[ ] License
[ ] Screenshots/demo (for visual projects)
```

### What to scan
```bash
# README existence and size
ls README.md README.rst README 2>/dev/null
wc -l README.md 2>/dev/null

# Docstring coverage (Python rough estimate)
total_funcs=$(grep -rn "def " --include="*.py" . | grep -v test | wc -l)
documented=$(grep -rn '"""' --include="*.py" . | wc -l)
echo "Rough docstring ratio: $documented / $total_funcs"

# LICENSE
ls LICENSE LICENSE.md COPYING 2>/dev/null

# CHANGELOG
ls CHANGELOG.md CHANGELOG HISTORY.md CHANGES.md 2>/dev/null
```

---

## 6. Freshness (Low Weight)

| Score | Criteria |
|-------|----------|
| 10 | Committed within 30 days. All deps on latest major. Runtime version current. |
| 8-9 | Committed within 90 days. Deps within 1 minor version of latest. |
| 6-7 | Committed within 6 months. Some deps 1+ major versions behind. |
| 4-5 | Committed within 1 year. Several outdated deps. |
| 2-3 | Committed 1-2 years ago. Many critically outdated deps. |
| 0-1 | Last commit 2+ years ago. Deps have known EOL. Runtime version unsupported. |

### What to scan
```bash
# Last commit
git log -1 --format="%ai %s"

# Commit frequency (past year)
git log --since="1 year ago" --oneline | wc -l

# Outdated deps
pip list --outdated 2>/dev/null        # Python
npm outdated 2>/dev/null               # Node
cargo outdated 2>/dev/null             # Rust

# Python version
python --version 2>&1
grep -r "python_requires" setup.py setup.cfg pyproject.toml 2>/dev/null

# Node version
node --version 2>&1
cat .nvmrc .node-version 2>/dev/null
grep '"engines"' package.json 2>/dev/null
```
