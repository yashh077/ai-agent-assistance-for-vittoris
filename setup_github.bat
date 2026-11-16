@echo off
echo =================================================================
echo 🚀 GITHUB REPOSITORY SETUP: ai-agent-assistance-for-vittoris
echo =================================================================

where git >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [!] Git is not installed on this system.
    echo Please install Git via PowerShell: winget install --id Git.Git -e
    echo Or download from: https://git-scm.com/download/win
    echo.
    pause
    exit /b 1
)

echo.
echo [1/4] Initializing git repository...
git init

echo [2/4] Staging files...
git add .
git commit -m "Initial commit: AI Agent Assistance for Vittoris"

echo [3/4] Setting main branch...
git branch -M main

echo.
set /p GH_USER="Enter your GitHub username: "
if not "%GH_USER%"=="" (
    git remote remove origin 2>nul
    git remote add origin https://github.com/%GH_USER%/ai-agent-assistance-for-vittoris.git
    echo.
    echo [4/4] Remote set to: https://github.com/%GH_USER%/ai-agent-assistance-for-vittoris.git
    echo.
    echo Now run: git push -u origin main
)

echo.
echo Done!
pause
