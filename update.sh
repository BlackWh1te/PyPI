#!/bin/bash
# Quick update script for ai-multitool
# Usage: ./update.sh "description of changes"

# Get description
DESCRIPTION="$1"

if [ -z "$DESCRIPTION" ]; then
    echo "Usage: ./update.sh \"description of changes\""
    echo "Example: ./update.sh \"Added analyze command\""
    exit 1
fi

# Add all changes
git add .

# Commit with description
git commit -m "$DESCRIPTION

Generated with [Devin](https://cli.devin.ai/docs)

Co-Authored-By: Devin <158243242+devin-ai-integration[bot]@users.noreply.github.com>"

# Push to main
git push origin main

echo "✅ Changes pushed to GitHub!"
