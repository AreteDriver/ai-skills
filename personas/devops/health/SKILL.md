# /health - Project Health Audit

Comprehensive project health check covering tests, coverage, dependencies, security, and documentation.

## Usage
```
/health                  # Full health audit
/health --quick          # Quick check (skip slow operations)
/health --fix            # Attempt to fix issues found
```

## What This Skill Does

1. **Test Health** - Run tests, check coverage percentage
2. **Dependency Health** - Outdated deps, security vulnerabilities
3. **Code Quality** - Lint issues, type coverage
4. **Documentation** - README, docstrings, CHANGELOG
5. **CI/CD** - Workflow existence and status
6. **Security** - Secrets scanning, dependency audit

## Health Report Format

```markdown
# Project Health Report: [Project Name]

## Summary
| Category | Status | Score |
|----------|--------|-------|
| Tests | Pass | 85% coverage |
| Dependencies | Warning | 3 outdated |
| Code Quality | Pass | No lint errors |
| Documentation | Warning | Missing CHANGELOG |
| Security | Pass | No vulnerabilities |

**Overall Health: Good (4/5)**

---

## Tests
- **Status**: Passing
- **Coverage**: 85% (target: 80%)
- **Test Count**: 127 tests
- **Issues**: None

## Dependencies
- **Outdated Packages**:
  - `requests`: 2.28.0 → 2.31.0 (minor)
  - `pytest`: 7.2.0 → 7.4.0 (minor)
- **Security Vulnerabilities**: None
- **Unused Dependencies**: None detected

## Code Quality
- **Lint Errors**: 0
- **Type Coverage**: 72%
- **Complexity Issues**: None

## Documentation
- [x] README.md exists
- [x] README has installation instructions
- [x] README has usage examples
- [ ] CHANGELOG.md missing
- [ ] API documentation incomplete

## CI/CD
- [x] GitHub Actions workflow exists
- [x] Tests run on PR
- [x] Lint checks enabled
- [ ] Coverage reporting not configured

## Security
- [x] No hardcoded secrets detected
- [x] No vulnerable dependencies
- [x] .gitignore excludes sensitive files

---

## Recommended Actions
1. **High**: Add CHANGELOG.md
2. **Medium**: Update 3 outdated dependencies
3. **Low**: Add coverage reporting to CI
```

## Checks Performed

### Tests
```bash
pytest --cov --cov-report=term-missing
```

### Dependencies
```bash
pip list --outdated
pip-audit  # if available
```

### Code Quality
```bash
ruff check .
mypy . --ignore-missing-imports
```

### Security
```bash
# Check for secrets
grep -r "password\|secret\|api_key" --include="*.py"
# Check .gitignore
cat .gitignore | grep -E "\.env|secret|credential"
```

## Instructions for Claude

When /health is invoked:

1. **Detect project type** - Python, Rust, TypeScript
2. **Run tests** - Capture pass/fail and coverage
3. **Check dependencies** - Outdated, vulnerable
4. **Run linter** - Collect errors/warnings
5. **Audit documentation** - README, CHANGELOG, docstrings
6. **Check CI** - Workflow files exist and are valid
7. **Security scan** - Secrets, .gitignore, permissions
8. **Generate report** - Summarize with actionable items
9. **Offer fixes** - If --fix flag, attempt automatic fixes
