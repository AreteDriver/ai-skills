# /readme - README Generator

Generate or update README.md from code analysis.

## Usage
```
/readme                  # Generate/update README
/readme --init           # Create new README from scratch
/readme --section install  # Update specific section
```

## What This Skill Does

1. **Analyze Project** - Detect type, dependencies, structure
2. **Extract Info** - From pyproject.toml, Cargo.toml, etc.
3. **Generate Sections** - Title, description, install, usage
4. **Add Badges** - CI status, version, license
5. **Write/Update** - Create or merge with existing

## README Structure

```markdown
# Project Name

[![CI](badge-url)](ci-url)
[![PyPI](badge-url)](pypi-url)
[![License](badge-url)](license-url)

Brief description of what this project does.

## Features

- Feature 1
- Feature 2
- Feature 3

## Installation

```bash
pip install project-name
```

## Quick Start

```python
from project import main
main()
```

## Usage

### Basic Usage
...

### Advanced Usage
...

## Configuration

| Option | Default | Description |
|--------|---------|-------------|
| opt1   | value   | What it does |

## Development

```bash
git clone https://github.com/user/repo
cd repo
pip install -e ".[dev]"
pytest
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md)

## License

MIT License - see [LICENSE](LICENSE)
```

## Badge Templates

```markdown
<!-- CI Status -->
[![CI](https://github.com/USER/REPO/actions/workflows/ci.yml/badge.svg)](https://github.com/USER/REPO/actions)

<!-- PyPI Version -->
[![PyPI](https://img.shields.io/pypi/v/PACKAGE)](https://pypi.org/project/PACKAGE/)

<!-- License -->
[![License](https://img.shields.io/github/license/USER/REPO)](LICENSE)

<!-- Python Version -->
[![Python](https://img.shields.io/pypi/pyversions/PACKAGE)](https://pypi.org/project/PACKAGE/)
```

## Instructions for Claude

When /readme is invoked:

1. **Detect project type** - Python, Rust, TypeScript, etc.
2. **Read config files** - pyproject.toml, Cargo.toml, package.json
3. **Extract metadata** - Name, version, description, license
4. **Analyze structure** - Main modules, entry points
5. **Check existing README** - Preserve custom content if updating
6. **Generate sections** - All standard sections
7. **Add badges** - CI, version, license
8. **Include examples** - From docstrings or tests
9. **Write file** - Create or update README.md
