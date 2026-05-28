# /package - Release Packaging Checklist

Guide through packaging for PyPI, crates.io, or npm.

## Usage
```
/package                 # Auto-detect and guide
/package pypi            # Python/PyPI packaging
/package crates          # Rust/crates.io packaging
/package npm             # Node/npm packaging
```

## What This Skill Does

1. **Audit Package Config** - Check pyproject.toml, Cargo.toml, package.json
2. **Validate Metadata** - Name, version, description, license, URLs
3. **Check Dependencies** - Pinned versions, security issues
4. **Verify Build** - Test the build process locally
5. **Generate Checklist** - Pre-publish verification steps

## PyPI Checklist

```markdown
## PyPI Release Checklist

### Metadata (pyproject.toml)
- [ ] `name` - Unique on PyPI, lowercase, hyphens
- [ ] `version` - Semantic versioning (X.Y.Z)
- [ ] `description` - One-line summary
- [ ] `readme` - Points to README.md
- [ ] `license` - SPDX identifier (MIT, Apache-2.0, etc.)
- [ ] `authors` - Name and email
- [ ] `urls.Homepage` - GitHub repo URL
- [ ] `urls.Documentation` - Docs URL (if any)
- [ ] `classifiers` - Python versions, license, status
- [ ] `requires-python` - Minimum Python version

### Dependencies
- [ ] All deps have version constraints
- [ ] No unused dependencies
- [ ] Dev deps in `[project.optional-dependencies]`

### Build Verification
- [ ] `pip install -e .` works
- [ ] `python -m build` succeeds
- [ ] `twine check dist/*` passes

### Pre-Publish
- [ ] Version bumped
- [ ] CHANGELOG updated
- [ ] Tests passing
- [ ] README accurate
- [ ] .gitignore includes dist/, *.egg-info/

### Publish Commands
```bash
python -m build
twine check dist/*
twine upload dist/*  # or use trusted publishing
```
```

## Crates.io Checklist

```markdown
## Crates.io Release Checklist

### Metadata (Cargo.toml)
- [ ] `name` - Unique on crates.io
- [ ] `version` - Semantic versioning
- [ ] `description` - One-line summary
- [ ] `license` - SPDX identifier
- [ ] `repository` - GitHub URL
- [ ] `documentation` - docs.rs or custom
- [ ] `keywords` - Up to 5 keywords
- [ ] `categories` - Valid crates.io categories

### Build Verification
- [ ] `cargo build --release` succeeds
- [ ] `cargo test` passes
- [ ] `cargo clippy` clean
- [ ] `cargo doc` builds

### Pre-Publish
- [ ] Version bumped in Cargo.toml
- [ ] CHANGELOG updated
- [ ] `cargo publish --dry-run` succeeds

### Publish
```bash
cargo publish
```
```

## Instructions for Claude

When /package is invoked:

1. **Detect package type** - pyproject.toml, Cargo.toml, package.json
2. **Audit metadata** - Check all required fields
3. **Identify issues** - Missing fields, invalid values
4. **Test build** - Run build commands
5. **Generate checklist** - Customized for the project
6. **Offer fixes** - Suggest or apply corrections
