@echo off
REM Quick update script for ai-multitool (Windows)
REM Usage: update.bat "description of changes"

if "%~1"=="" (
    echo Usage: update.bat "description of changes"
    echo Example: update.bat "Added analyze command"
    exit /b 1
)

set DESCRIPTION=%~1

REM Add all changes
git add .

REM Commit with description
git commit -m "%DESCRIPTION%

Generated with [Devin](https://cli.devin.ai/docs)

Co-Authored-By: Devin <158243242+devin-ai-integration[bot]@users.noreply.github.com>"

REM Push to main
git push origin main

echo Changes pushed to GitHub!
