# AGSR-GDAC Institutional Deployment Script
# Target: Global Primary Node (Nairobi)

Write-Host "--- INITIATING SECURE DEPLOYMENT SEQUENCE ---" -ForegroundColor Cyan

# 1. Clean Local Bloat
Write-Host "[1/3] Scrubbing local cache..." -ForegroundColor Yellow
if (Test-Path "__pycache__") { Remove-Item -Recurse -Force "__pycache__" }

# 2. Institutional Git Staging
Write-Host "[2/3] Staging node infrastructure..." -ForegroundColor Yellow
git add .

# 3. Final Sovereign Commit & Push
$commitMsg = "DEPLOY: Primary Node Active | Base L2 Treasury: 0x501E5...86FbF | Location: Nairobi"
Write-Host "[3/3] Committing to Global Registry..." -ForegroundColor Yellow
git commit -m "$commitMsg"

Write-Host ">>> PUSHING TO RENDER CLOUD..." -ForegroundColor Green
git push

Write-Host "--- DEPLOYMENT COMMAND SENT ---" -ForegroundColor Cyan
Write-Host "Check your Render Dashboard to monitor the build."