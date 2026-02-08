# Deploy Helper Script
Write-Host "🚀 Preparing for Manual Deployment..." -ForegroundColor Cyan

# 1. Open GitHub New Repo Page
Write-Host "1. Opening GitHub..."
Start-Process "https://github.com/new"

# 2. Open Project Folder
Write-Host "2. Opening Project Folder..."
Invoke-Item "."

# 3. Instructions
Write-Host "`n✅ ACTION REQUIRED:" -ForegroundColor Yellow
Write-Host "1. Create a new repository on GitHub."
Write-Host "2. Click 'Upload files' in the new repo."
Write-Host "3. Drag and drop the contents of 'Air_Quality_Platform_v2.zip' (extract it first!) or the project files."
Write-Host "4. Commit changes."
Write-Host "`nPress any key to exit..."
Read-Host
