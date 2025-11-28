#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Pre-publication security cleanup script
.DESCRIPTION
    Prepares repository for public release by removing sensitive data from documentation
#>

$ErrorActionPreference = "Stop"

Write-Host "`n🔒 PRE-PUBLICATION SECURITY CLEANUP" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Gray
Write-Host ""

# Your actual values to replace (update these!)
$REAL_CLIENT_ID = "bcb41e64-e9a8-421c-9331-699dd9041d58"
$REAL_OPENAI_RESOURCE = "ca-policy-manager-helper"

# Safe placeholder values
$PLACEHOLDER_CLIENT_ID = "<your-client-id-here>"
$PLACEHOLDER_OPENAI_RESOURCE = "<your-resource-name>"

Write-Host "⚠️  WARNING: This will replace real values with placeholders" -ForegroundColor Yellow
Write-Host "   Real Client ID: $REAL_CLIENT_ID" -ForegroundColor Gray
Write-Host "   Real OpenAI Resource: $REAL_OPENAI_RESOURCE" -ForegroundColor Gray
Write-Host ""
Write-Host "   Press CTRL+C to cancel, or" -ForegroundColor Yellow
$confirm = Read-Host "   Type 'YES' to continue"

if ($confirm -ne 'YES') {
    Write-Host "❌ Cancelled" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "📝 Step 1: Backing up files..." -ForegroundColor Cyan
$backupFolder = "pre-publication-backup-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
New-Item -ItemType Directory -Path $backupFolder -Force | Out-Null

# Files that might contain real values
$filesToCheck = @(
    "README.md",
    "CA_Policy_Manager_Web/.env.example",
    "CA_Policy_Manager_Web/AI_SETUP_GUIDE.md",
    "CA_Policy_Manager_Web/QUICKSTART.md",
    "docs/**/*.md"
)

$filesModified = @()

Write-Host ""
Write-Host "📝 Step 2: Replacing sensitive values..." -ForegroundColor Cyan

foreach ($pattern in $filesToCheck) {
    $files = Get-ChildItem -Path $pattern -File -Recurse -ErrorAction SilentlyContinue
    
    foreach ($file in $files) {
        $content = Get-Content $file.FullName -Raw
        $originalContent = $content
        
        # Replace Client ID
        $content = $content -replace [regex]::Escape($REAL_CLIENT_ID), $PLACEHOLDER_CLIENT_ID
        
        # Replace OpenAI resource name
        $content = $content -replace "$REAL_OPENAI_RESOURCE\.openai\.azure\.com", "$PLACEHOLDER_OPENAI_RESOURCE.openai.azure.com"
        
        if ($content -ne $originalContent) {
            # Backup original
            $backupPath = Join-Path $backupFolder $file.Name
            Copy-Item $file.FullName $backupPath -Force
            
            # Write cleaned version
            Set-Content -Path $file.FullName -Value $content -NoNewline
            
            Write-Host "  ✓ Cleaned: $($file.FullName)" -ForegroundColor Green
            $filesModified += $file.FullName
        }
    }
}

Write-Host ""
Write-Host "📝 Step 3: Verifying .env is not tracked..." -ForegroundColor Cyan
$envInGit = git ls-files "*/.env" 2>$null
if ($envInGit -and $envInGit -notmatch "\.env\.example") {
    Write-Host "❌ ERROR: .env file is tracked by git!" -ForegroundColor Red
    Write-Host "   Run: git rm --cached CA_Policy_Manager_Web/.env" -ForegroundColor Yellow
    exit 1
}
else {
    Write-Host "  ✓ .env is not tracked" -ForegroundColor Green
}

Write-Host ""
Write-Host "📝 Step 4: Final security checks..." -ForegroundColor Cyan

# Check for any remaining real values in tracked files
$stillPresent = git ls-files | ForEach-Object {
    $content = Get-Content $_ -Raw -ErrorAction SilentlyContinue
    if ($content -match [regex]::Escape($REAL_CLIENT_ID)) {
        $_
    }
}

if ($stillPresent) {
    Write-Host "⚠️  Real Client ID still found in:" -ForegroundColor Yellow
    $stillPresent | ForEach-Object { Write-Host "     $_" -ForegroundColor Gray }
}
else {
    Write-Host "  ✓ No real Client ID found in tracked files" -ForegroundColor Green
}

Write-Host ""
Write-Host "=" * 60 -ForegroundColor Gray
Write-Host "✅ CLEANUP COMPLETE" -ForegroundColor Green
Write-Host "=" * 60 -ForegroundColor Gray
Write-Host ""
Write-Host "📊 Summary:" -ForegroundColor Cyan
Write-Host "  Modified files: $($filesModified.Count)" -ForegroundColor White
Write-Host "  Backups saved to: $backupFolder" -ForegroundColor White
Write-Host ""
Write-Host "⚠️  CRITICAL NEXT STEPS:" -ForegroundColor Yellow
Write-Host "  1. Review changes: git diff" -ForegroundColor Gray
Write-Host "  2. Rotate Azure OpenAI API key in Azure Portal" -ForegroundColor Gray
Write-Host "  3. Update your local .env with new key" -ForegroundColor Gray
Write-Host "  4. Verify: git status | Select-String '.env'" -ForegroundColor Gray
Write-Host "  5. Commit changes: git add . && git commit -m 'Security: Remove sensitive data'" -ForegroundColor Gray
Write-Host ""
Write-Host "📖 See PRE_PUBLICATION_SECURITY_REPORT.md for full checklist" -ForegroundColor Cyan
