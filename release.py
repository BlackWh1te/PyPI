#!/usr/bin/env python3
"""
Release automation script for ai-multitool
Automates: changelog update, version bump, git commit, and push
"""

import re
import subprocess
import sys
from pathlib import Path
from typing import List


def run_command(cmd: List[str], check: bool = True) -> str:
    """Run a shell command and return output"""
    result = subprocess.run(cmd, capture_output=True, text=True, check=check)
    return result.stdout + result.stderr


def get_current_version() -> str:
    """Get current version from __init__.py"""
    init_file = Path("ai_multitool/__init__.py")
    content = init_file.read_text()
    match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', content)
    if match:
        return match.group(1)
    raise ValueError("Could not find version in __init__.py")


def bump_version(version: str, bump_type: str = "patch") -> str:
    """Bump version (major, minor, patch)"""
    parts = version.split(".")
    if len(parts) != 3:
        raise ValueError(f"Invalid version format: {version}")

    major, minor, patch = int(parts[0]), int(parts[1]), int(parts[2])

    if bump_type == "major":
        major += 1
        minor = 0
        patch = 0
    elif bump_type == "minor":
        minor += 1
        patch = 0
    elif bump_type == "patch":
        patch += 1
    else:
        raise ValueError(f"Invalid bump type: {bump_type}")

    return f"{major}.{minor}.{patch}"


def update_version(new_version: str):
    """Update version in __init__.py"""
    init_file = Path("ai_multitool/__init__.py")
    content = init_file.read_text()
    content = re.sub(
        r'__version__\s*=\s*["\'][^"\']+["\']',
        f'__version__ = "{new_version}"',
        content
    )
    init_file.write_text(content)
    print(f"✅ Updated version to {new_version}")


def update_changelog(version: str, changes: str):
    """Update docs/CHANGELOG.md with new version"""
    changelog_file = Path("docs/CHANGELOG.md")

    if changelog_file.exists():
        content = changelog_file.read_text()
    else:
        content = "# Changelog\n\nAll notable changes to ai-multitool will be documented in this file.\n"

    # Add new version entry
    new_entry = f"\n## [{version}] - {get_current_date()}\n\n{changes}\n"
    content = content.replace("## [Unreleased]", f"## [Unreleased]\n{new_entry}")

    changelog_file.write_text(content)
    print(f"✅ Updated docs/CHANGELOG.md for version {version}")


def get_current_date() -> str:
    """Get current date in YYYY-MM-DD format"""
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d")


def git_commit(version: str, message: str = None):
    """Commit changes with version tag"""
    if message is None:
        message = f"Release v{version}"

    # Add all changes
    run_command(["git", "add", "."])

    # Commit
    commit_msg = f"{message}\n\nGenerated with [Devin](https://cli.devin.ai/docs)\n\nCo-Authored-By: Devin <158243242+devin-ai-integration[bot]@users.noreply.github.com>"
    run_command(["git", "commit", "-m", commit_msg])
    print(f"✅ Committed changes")

    # Create tag
    run_command(["git", "tag", f"v{version}"])
    print(f"✅ Created tag v{version}")


def git_push():
    """Push to GitHub"""
    run_command(["git", "push", "origin", "main"])
    run_command(["git", "push", "origin", "--tags"])
    print("✅ Pushed to GitHub")


def release(bump_type: str = "patch", changes: str = None):
    """
    Perform a complete release:
    1. Bump version
    2. Update CHANGELOG
    3. Commit changes
    4. Push to GitHub
    """
    print(f"\n🚀 Starting release (bump: {bump_type})...\n")

    # Get current version
    current_version = get_current_version()
    print(f"Current version: {current_version}")

    # Bump version
    new_version = bump_version(current_version, bump_type)
    print(f"New version: {new_version}")

    # Update version in code
    update_version(new_version)

    # Update changelog
    if changes is None:
        changes = input("\nEnter changelog entries (one per line, empty line to finish):\n")
        if changes:
            changes = "\n".join([f"### Added\n- {line}" for line in changes.split("\n") if line.strip()])
    update_changelog(new_version, changes or "### Added\n- Bug fixes and improvements")

    # Commit and push
    git_commit(new_version)
    git_push()

    print(f"\n✅ Release v{new_version} complete!")
    print(f"📦 View at: https://github.com/BlackWh1te/PyPi/releases/tag/v{new_version}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python release.py [patch|minor|major] [changes]")
        print("Example: python release.py patch \"Added new feature\"")
        sys.exit(1)

    bump_type = sys.argv[1]
    changes = sys.argv[2] if len(sys.argv) > 2 else None

    if bump_type not in ["patch", "minor", "major"]:
        print("Error: bump_type must be 'patch', 'minor', or 'major'")
        sys.exit(1)

    try:
        release(bump_type, changes)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
