---
name: build
description: Build and install the project in development mode. Handles venv creation and editable installs. Invoke with /build.
lifecycle: experimental
---

# Build Skill

Build and install the project for development.

## Usage

```
/build           # Install in dev mode
/build --clean   # Clean and reinstall
/build --prod    # Build distribution
```

## Process

1. **Setup virtual environment**
   ```bash
   # Create venv if not exists
   [ -d .venv ] || python3 -m venv .venv

   # Activate
   source .venv/bin/activate
   ```

2. **Install dependencies**
   ```bash
   # Upgrade pip
   pip install --upgrade pip

   # Install in editable mode with dev deps
   pip install -e ".[dev]"
   # Or without dev deps
   pip install -e .
   ```

3. **Verify installation**
   ```bash
   # Check package is installed
   pip show <package-name>

   # Run quick test
   python -c "import <package>; print(<package>.__version__)"
   ```

## Quick Commands

```bash
# Full setup from scratch
python3 -m venv .venv && source .venv/bin/activate && pip install -e ".[dev]"

# Just reinstall
pip install -e . --force-reinstall

# Build distribution
pip install build && python -m build

# Check what would be installed
pip install -e . --dry-run
```

## Build Distribution

```bash
# Build wheel and sdist
pip install build
python -m build

# Output in dist/
ls dist/
# package-1.0.0-py3-none-any.whl
# package-1.0.0.tar.gz

# Test install from wheel
pip install dist/*.whl
```

## Troubleshooting

- **No pyproject.toml**: Create one or use setup.py
- **Missing deps**: Check [project.dependencies] in pyproject.toml
- **Import errors after install**: Try `pip install -e . --force-reinstall`
- **Conflicting versions**: `pip install --upgrade-strategy eager -e .`

## Output

```
Installing: my-package (editable)
Successfully installed my-package-1.0.0 dep1-2.0 dep2-3.0

Installed entry points:
  my-cli = my_package.cli:main

Ready for development!
```
