---
title: AI Skills Dependency Snapshot
source_id: SRC-AIS-REPO-003
status: active
authority: high
owner: Engineering
date_created: 2026-06-18
date_collected: 2026-06-18
current: true
sensitive: false
related_documents:
  - docs/06-installation-operations-and-support.md
---

# Dependency Snapshot

## Runtime and Development Dependencies

| Dependency | Version Policy Seen | Used By | Current Concern | Recommended Control |
|---|---|---|---|---|
| Bash | `>=4` claimed in `CLAUDE.md`; installer comments claim Bash 3.2 compatibility | Installer and checks | Contradictory portability claims | Test Bash 3.2 and 5.x or adopt Python CLI |
| Python | `3.x` in CI | YAML parsing and metadata helper | Unbounded version | Support explicit floor and CI matrix |
| PyYAML | Unpinned `pip install pyyaml` | CI validation | Non-reproducible | Pin compatible range and lock CI |
| `actions/checkout` | Major tag | CI | Mutable tag | Pin commit SHA or trusted major with Dependabot |
| `actions/setup-python` | Major tag | CI | Mutable tag | Pin commit SHA or trusted major |
| Claude Code | No tested range | Runtime target | Compatibility assertions unverified | Add adapter contract and version matrix |
| OpenClaw metadata | Format checked | Optional target | Coupled into every skill validator | Move to adapter-specific validation |
| GitHub | Required for source and CI | Distribution | No release artifact integrity model | Signed releases and checksums |
| Docker | Skill-specific | Sandboxed execution | Environment assumption | Capability declaration and optional test lane |

## Dependency Design Recommendation

The repository should have a small, explicit toolchain:

- Python 3.11+ CLI and validation package
- `pydantic` or `jsonschema`
- `ruamel.yaml` or PyYAML
- `pytest`
- `pytest-cov`
- `ruff`
- `mypy` or pyright
- optional `shellcheck` for remaining shell scripts
- `markdownlint-cli2` for documentation
- `pip-audit` or equivalent for supply-chain checks

Use a `pyproject.toml` and lockfile. Avoid duplicating catalog logic in Bash.
