#!/usr/bin/env python3
"""Integration tests for tools/install.sh

Covers: dry-run, install, uninstall, list, preview for all bundles.
"""

import json
import os
import subprocess
import tempfile
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
INSTALLER = REPO_ROOT / "tools" / "install.sh"
RESOLVER = REPO_ROOT / "scripts" / "resolve-bundle.py"


def run(*args, env=None, check=True):
    """Run install.sh with given args."""
    full_env = {**os.environ, **(env or {})}
    result = subprocess.run(
        [str(INSTALLER), *args],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
        env=full_env,
    )
    if check and result.returncode != 0:
        raise AssertionError(
            f"install.sh {' '.join(args)} failed with {result.returncode}:\n"
            f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
        )
    return result


def all_bundles():
    """Return all bundle names from bundles.yaml."""
    result = subprocess.run(
        ["python3", str(RESOLVER), "--list"],
        capture_output=True,
        text=True,
        check=True,
    )
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


BUNDLES = all_bundles()


class TestDryRun:
    """Dry-run should never touch the filesystem."""

    @pytest.mark.parametrize("bundle", BUNDLES)
    def test_dry_run_no_files_created(self, bundle):
        with tempfile.TemporaryDirectory() as td:
            env = {
                "CLAUDE_SKILLS_DIR": f"{td}/skills",
                "AI_SKILLS_MANIFESTS_DIR": f"{td}/manifests",
            }
            result = run("--bundle", bundle, "--dry-run", env=env)
            assert result.returncode == 0
            assert "would install" in result.stdout or "Dry run complete" in result.stdout
            # Nothing should be written
            assert not Path(td, "skills").exists() or not any(Path(td, "skills").iterdir())
            assert not Path(td, "manifests").exists() or not any(Path(td, "manifests").iterdir())


class TestInstall:
    """Actual install + manifest generation."""

    @pytest.mark.parametrize("bundle", BUNDLES)
    def test_install_writes_skills_and_manifest(self, bundle):
        with tempfile.TemporaryDirectory() as td:
            env = {
                "CLAUDE_SKILLS_DIR": f"{td}/skills",
                "AI_SKILLS_MANIFESTS_DIR": f"{td}/manifests",
            }
            result = run("--bundle", bundle, env=env)
            assert result.returncode == 0
            assert "installed" in result.stdout

            # Manifest must exist
            manifests = list(Path(td, "manifests").glob(f"{bundle}-*.json"))
            assert len(manifests) == 1, f"Expected 1 manifest for {bundle}, found {manifests}"

            manifest = json.loads(manifests[0].read_text())
            assert manifest["bundle"] == bundle
            assert "installed_at" in manifest
            assert "skills" in manifest

            # Every skill in manifest must exist on disk
            for skill in manifest["skills"]:
                dest = Path(skill["dest"])
                assert dest.exists(), f"Missing installed skill: {dest}"
                assert (dest / "SKILL.md").exists(), f"Missing SKILL.md in {dest}"

            # Hooks list (not auto-installed) should be present in manifest if any
            assert "hooks" in manifest


class TestUninstall:
    """Bundle uninstall removes exactly what it installed."""

    @pytest.mark.parametrize("bundle", BUNDLES)
    def test_uninstall_removes_skills(self, bundle):
        with tempfile.TemporaryDirectory() as td:
            env = {
                "CLAUDE_SKILLS_DIR": f"{td}/skills",
                "AI_SKILLS_MANIFESTS_DIR": f"{td}/manifests",
            }
            # Install
            run("--bundle", bundle, env=env)

            # Capture installed skills
            skills_dir = Path(td, "skills")
            before = set(p.name for p in skills_dir.iterdir())
            assert before

            # Uninstall
            result = run("--uninstall", bundle, env=env)
            assert result.returncode == 0
            assert "Uninstalled" in result.stdout

            # Skills should be gone
            after = set(p.name for p in skills_dir.iterdir()) if skills_dir.exists() else set()
            removed = before - after
            assert removed == before, f"Expected all skills removed, but {after} remain"

            # Manifest should be removed
            manifests = list(Path(td, "manifests").glob(f"{bundle}-*.json"))
            assert len(manifests) == 0, f"Manifest still exists after uninstall: {manifests}"

    def test_uninstall_no_manifest_shows_error(self):
        with tempfile.TemporaryDirectory() as td:
            env = {
                "CLAUDE_SKILLS_DIR": f"{td}/skills",
                "AI_SKILLS_MANIFESTS_DIR": f"{td}/manifests",
            }
            result = run("--uninstall", "nonexistent-bundle", env=env, check=False)
            assert result.returncode != 0
            assert "No manifest found" in result.stdout or "No manifest found" in result.stderr


class TestList:
    """--list should enumerate skills and bundles."""

    def test_list_shows_bundles(self):
        result = run("--list")
        for bundle in BUNDLES:
            assert bundle in result.stdout, f"Bundle {bundle} missing from --list"

    def test_list_shows_personas(self):
        result = run("--list")
        # At least one known persona should appear
        assert "code-reviewer" in result.stdout or "senior-software-engineer" in result.stdout

    def test_list_shows_agents(self):
        result = run("--list")
        # At least one known agent should appear
        assert "handoff" in result.stdout or "browser-automation" in result.stdout


class TestPreview:
    """--preview should show bundle contents without installing."""

    @pytest.mark.parametrize("bundle", BUNDLES)
    def test_preview_no_side_effects(self, bundle):
        with tempfile.TemporaryDirectory() as td:
            env = {
                "CLAUDE_SKILLS_DIR": f"{td}/skills",
                "AI_SKILLS_MANIFESTS_DIR": f"{td}/manifests",
            }
            result = run("--bundle", bundle, "--preview", env=env)
            assert result.returncode == 0
            assert "Previewing" in result.stdout or "would install" in result.stdout
            # Nothing written
            assert not Path(td, "skills").exists() or not any(Path(td, "skills").iterdir())


class TestInstallAll:
    """--all should install everything."""

    def test_all_installs_personas_agents_workflows_hooks(self):
        with tempfile.TemporaryDirectory() as td:
            env = {
                "CLAUDE_SKILLS_DIR": f"{td}/skills",
                "AI_SKILLS_MANIFESTS_DIR": f"{td}/manifests",
                "CLAUDE_HOOKS_DIR": f"{td}/hooks",
            }
            result = run("--all", env=env)
            assert result.returncode == 0
            skills = list(Path(td, "skills").iterdir())
            assert len(skills) > 50, f"Expected >50 skills, got {len(skills)}"
            hooks = list(Path(td, "hooks").glob("*.sh"))
            assert len(hooks) > 0, "Expected hooks to be installed"
