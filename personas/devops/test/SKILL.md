---
name: test
description: Run pytest with coverage summary. Provides quick feedback on test status and coverage. Invoke with /test or /test <path>.
lifecycle: experimental
---

# Test Skill

Run project tests with pytest and show coverage summary.

## Usage

```
/test                    # Run all tests
/test tests/test_foo.py  # Run specific file
/test -k "test_name"     # Run matching tests
/test --cov              # With coverage report
```

## Process

1. **Detect test framework**
   ```bash
   # Check for pytest
   [ -f pyproject.toml ] && grep -q pytest pyproject.toml && echo "pytest"
   [ -f setup.cfg ] && grep -q pytest setup.cfg && echo "pytest"
   [ -d tests ] && echo "has tests dir"
   ```

2. **Run tests with coverage**
   ```bash
   # Activate venv if exists
   [ -d .venv ] && source .venv/bin/activate

   # Run pytest with coverage
   pytest -v --tb=short --cov=src --cov-report=term-missing

   # Or minimal run
   pytest -v --tb=short
   ```

3. **Report summary**
   - Total tests: passed/failed/skipped
   - Coverage percentage
   - Failed test names if any

## Quick Commands

```bash
# Fast run (no coverage)
pytest -x -q

# With coverage
pytest --cov=. --cov-report=term-missing

# Specific test
pytest tests/test_foo.py::TestClass::test_method -v

# Run failed tests only
pytest --lf

# Run tests matching pattern
pytest -k "test_login or test_auth"
```

## Output Format

```
===== test session starts =====
collected 45 items

tests/test_core.py ........ [18%]
tests/test_api.py ......... [38%]
tests/test_ui.py .......... [60%]

===== 45 passed in 2.34s =====

Coverage: 87%
Missing: src/utils.py:45-50, src/api.py:120
```

## Troubleshooting

- **No tests found**: Check pytest.ini or pyproject.toml for testpaths
- **Import errors**: Ensure `pip install -e .` was run
- **Qt tests failing**: Use `QT_QPA_PLATFORM=offscreen pytest`
