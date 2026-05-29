---
name: ci
description: GitHub Actions Workflow Generator
---

# /ci - GitHub Actions Workflow Generator

Generate and update GitHub Actions CI/CD workflows.

## Usage
```
/ci                      # Analyze project, suggest workflows
/ci python               # Python CI workflow
/ci rust                 # Rust CI workflow
/ci release              # Release automation workflow
/ci --fix                # Fix existing workflow issues
```

## What This Skill Does

1. **Detect Project Type** - Python, Rust, TypeScript, etc.
2. **Analyze Dependencies** - Package manager, test framework, linter
3. **Generate Workflow** - Create appropriate .github/workflows/*.yml
4. **Best Practices** - Caching, matrix builds, security

## Workflow Templates

### Python CI
```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pip install ruff
      - run: ruff check .
      - run: ruff format --check .

  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.10", "3.11", "3.12"]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
      - run: pip install -e ".[dev]"
      - run: pytest --cov --cov-report=xml
      - uses: codecov/codecov-action@v4
        if: matrix.python-version == '3.11'
```

### Rust CI
```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: dtolnay/rust-toolchain@stable
        with:
          components: rustfmt, clippy
      - uses: Swatinem/rust-cache@v2
      - run: cargo fmt --check
      - run: cargo clippy -- -D warnings
      - run: cargo test
```

### Release Workflow
```yaml
name: Release

on:
  push:
    tags: ["v*"]

jobs:
  release:
    runs-on: ubuntu-latest
    permissions:
      contents: write
      id-token: write
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pip install build twine
      - run: python -m build
      - uses: pypa/gh-action-pypi-publish@release/v1
      - uses: softprops/action-gh-release@v1
        with:
          files: dist/*
          generate_release_notes: true
```

## Instructions for Claude

When /ci is invoked:

1. **Detect project type** - Check for pyproject.toml, Cargo.toml, package.json
2. **Identify tools** - Test framework, linter, formatter
3. **Check existing workflows** - Don't duplicate, update if needed
4. **Use caching** - Speed up builds with dependency caching
5. **Matrix builds** - Test multiple versions where appropriate
6. **Security** - Use pinned action versions, minimal permissions
7. **Create .github/workflows/** - Write the workflow file(s)
