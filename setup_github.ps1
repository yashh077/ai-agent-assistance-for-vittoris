# Setup and push script for GitHub repository: ai-agent-assistance-for-vittoris
param(
    [Parameter(Mandatory=$false)]
    [string]$GitHubUsername = ""
)

Write-Host "=================================================================" -ForegroundColor Cyan
Write-Host "🚀 GITHUB REPOSITORY SETUP FOR: ai-agent-assistance-for-vittoris" -ForegroundColor Cyan
Write-Host "=================================================================" -ForegroundColor Cyan

# 1. Check Git
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Host "`n⚠️ Git is not currently installed or not in your PATH." -ForegroundColor Yellow
    Write-Host "You can install it easily with one command in PowerShell:" -ForegroundColor White
    Write-Host "   winget install --id Git.Git -e --source winget`n" -ForegroundColor Green
    Write-Host "Or download it from: https://git-scm.com/download/win" -ForegroundColor White
    exit 1
}

# 2. Initialize Git
Write-Host "`n[1/4] Initializing local git repository..." -ForegroundColor Yellow
git init

# 3. Add and commit files
Write-Host "[2/4] Staging project files..." -ForegroundColor Yellow
git add .
git commit -m "Initial commit: AI Agent Assistance for Vittoris (Autonomous Ops & Voice Agent)"

# 4. Set main branch
Write-Host "[3/4] Renaming branch to main..." -ForegroundColor Yellow
git branch -M main

# 5. Remote and Push
if ($GitHubUsername -eq "") {
    $GitHubUsername = Read-Host "`nEnter your GitHub username (e.g. 'octocat')"
}

if ($GitHubUsername -ne "") {
    $remoteUrl = "https://github.com/$GitHubUsername/ai-agent-assistance-for-vittoris.git"
    Write-Host "`n[4/4] Adding remote origin: $remoteUrl" -ForegroundColor Yellow
    
    # Remove existing origin if any
    git remote remove origin -ErrorAction SilentlyContinue
    git remote add origin $remoteUrl

    Write-Host "`nTo push your code to GitHub, run:" -ForegroundColor Green
    Write-Host "   git push -u origin main`n" -ForegroundColor White
} else {
    Write-Host "`nSkipped remote configuration. You can add it later using:" -ForegroundColor Yellow
    Write-Host "   git remote add origin https://github.com/<YOUR-USERNAME>/ai-agent-assistance-for-vittoris.git"
    Write-Host "   git push -u origin main"
}

Write-Host "=================================================================" -ForegroundColor Cyan
Write-Host "🎉 Local repository prepared successfully!" -ForegroundColor Green
Write-Host "=================================================================" -ForegroundColor Cyan
