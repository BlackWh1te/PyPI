# Development Workflow Guide

This guide explains how to use the automation scripts for updating the project after each change.

## Quick Update (Recommended for Minor Changes)

For small updates, bug fixes, or incremental features, use the quick update script:

### Windows
```bash
update.bat "description of changes"
```

### Linux/Mac
```bash
chmod +x update.sh
./update.sh "description of changes"
```

**Example:**
```bash
update.bat "Added analyze command with file reading"
```

This will:
1. Add all changed files to git
2. Commit with the description
3. Push to GitHub main branch

## Full Release (For Major Features or Version Bumps)

For significant features or when you want to create a new version release:

```bash
python release.py [patch|minor|major] "changelog entries"
```

**Bump Types:**
- `patch` - Bug fixes, small improvements (0.1.0 → 0.1.1)
- `minor` - New features, backward compatible (0.1.0 → 0.2.0)
- `major` - Breaking changes (0.1.0 → 1.0.0)

**Examples:**
```bash
# Patch release
python release.py patch "Fixed bug in chat command"

# Minor release
python release.py minor "Added vector search capabilities"

# Major release
python release.py major "Complete rewrite with new architecture"
```

This will:
1. Bump the version in `ai_multitool/__init__.py`
2. Update `CHANGELOG.md` with new version entry
3. Commit all changes
4. Create git tag (e.g., v0.1.1)
5. Push to GitHub with tags

## Manual Workflow

If you prefer manual control:

### 1. Make Your Changes
Edit files as needed

### 2. Update CHANGELOG.md
Add your changes under the `[Unreleased]` section:

```markdown
## [Unreleased]

### Added
- Your new feature here

### Fixed
- Bug you fixed here

### Changed
- Something you changed here
```

### 3. Update Version (Optional)
Edit `ai_multitool/__init__.py`:
```python
__version__ = "0.1.1"  # Bump this
```

### 4. Commit Changes
```bash
git add .
git commit -m "Your commit message"
```

### 5. Push to GitHub
```bash
git push origin main
```

### 6. Create Release (Optional)
Go to GitHub → Releases → Create new release
- Tag version: v0.1.1
- Title: Release v0.1.1
- Description: Copy from CHANGELOG

## Workflow Examples

### Scenario 1: Quick Bug Fix
```bash
# Fix the bug
# Run quick update
update.bat "Fixed crash in chat command when stream=True"
```

### Scenario 2: Adding a New Feature
```bash
# Implement the feature
# Update CHANGELOG.md manually
# Run quick update
update.bat "Added analyze command with code parsing"
```

### Scenario 3: Major Feature Release
```bash
# Implement the feature
# Run full release
python release.py minor "Added vector search with RAG capabilities"
```

### Scenario 4: Breaking Changes
```bash
# Make breaking changes
# Run major release
python release.py major "Redesigned CLI interface, breaking changes in commands"
```

## Best Practices

1. **Always describe changes clearly** - Use descriptive commit messages
2. **Update CHANGELOG.md** - Keep track of what changed
3. **Test before pushing** - Ensure your changes work
4. **Use semantic versioning** - Follow semver for version bumps
5. **Create releases for milestones** - Use GitHub releases for significant versions

## Git Branch Strategy

Currently using:
- **main** - Production branch, always deployable

For larger projects, consider:
- **main** - Production
- **develop** - Development
- **feature/*** - Feature branches

## Troubleshooting

### Push Fails
```bash
# Pull latest changes first
git pull origin main --rebase
# Then push again
git push origin main
```

### Commit Fails
```bash
# Check what's not committed
git status
# Add files if needed
git add .
# Try commit again
```

### Version Bump Fails
```bash
# Check current version
python -c "from ai_multitool import __version__; print(__version__)"
# Manually edit ai_multitool/__init__.py if needed
```

## Automation Scripts Reference

### update.bat / update.sh
**Purpose:** Quick updates without version bumping
**Use when:** Bug fixes, documentation updates, small changes
**Does:** git add, commit, push

### release.py
**Purpose:** Full release with version bumping
**Use when:** New features, significant changes, version releases
**Does:** Version bump, CHANGELOG update, git tag, commit, push

## GitHub Repository
- **URL:** https://github.com/BlackWh1te/PyPI.git
- **Branch:** main
- **Current Version:** 0.1.0

## Next Steps

After pushing changes:
1. Monitor GitHub Actions (if configured)
2. Check that the release is live
3. Update documentation if needed
4. Announce new features (optional)
