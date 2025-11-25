#!/usr/bin/env pwsh
# cleanup_for_github.ps1
# Prepares repository for GitHub publication by removing sensitive files

Write-Host "`n🧹 Cleaning up repository for GitHub publication..." -ForegroundColor Cyan
Write-Host "============================================`n" -ForegroundColor Cyan

$rootPath = $PSScriptRoot
Set-Location $rootPath

# Track what was deleted
$deletedFiles = @()
$deletedDirs = @()
$errors = @()

function Remove-ItemSafely {
    param(
        [string]$Path,
        [switch]$Recurse
    )
    
    if (Test-Path $Path) {
        try {
            if ($Recurse) {
                Remove-Item -Path $Path -Recurse -Force -ErrorAction Stop
                $deletedDirs += $Path
            } else {
                Remove-Item -Path $Path -Force -ErrorAction Stop
                $deletedFiles += $Path
            }
            Write-Host "✓ Removed: $Path" -ForegroundColor Green
        } catch {
            $errors += "Failed to remove $Path : $_"
            Write-Host "✗ Failed to remove: $Path" -ForegroundColor Red
        }
    }
}

Write-Host "📂 Cleaning root directory..." -ForegroundColor Yellow

# Root directory cleanup
Remove-ItemSafely ".venv" -Recurse
Remove-ItemSafely "__pycache__" -Recurse
Remove-ItemSafely "web_data" -Recurse
Remove-ItemSafely "ca_policies_backup.json"
Remove-ItemSafely "Microsoft_Defender_Policies.xlsx"

Write-Host "`n📂 Cleaning CA_Policy_Manager_Web..." -ForegroundColor Yellow

# CA_Policy_Manager_Web cleanup
if (Test-Path "CA_Policy_Manager_Web") {
    Set-Location "CA_Policy_Manager_Web"
    
    # CRITICAL: Remove environment files
    Remove-ItemSafely ".env"
    Remove-ItemSafely ".env.azure"
    
    # Remove temporary/generated files
    Remove-ItemSafely "organize_folder.ps1"
    Remove-ItemSafely "SETUP_COMPLETE.md"
    Remove-ItemSafely "__pycache__" -Recurse
    
    # Clean data directories but keep structure
    if (Test-Path "data/uploads") {
        Get-ChildItem "data/uploads" -Exclude ".gitkeep" | ForEach-Object {
            Remove-ItemSafely $_.FullName
        }
        
        # Ensure .gitkeep exists
        if (-not (Test-Path "data/uploads/.gitkeep")) {
            New-Item "data/uploads/.gitkeep" -ItemType File -Force | Out-Null
            Write-Host "✓ Created: data/uploads/.gitkeep" -ForegroundColor Green
        }
    }
    
    if (Test-Path "data/backups") {
        Get-ChildItem "data/backups" -Exclude ".gitkeep" | ForEach-Object {
            Remove-ItemSafely $_.FullName
        }
        
        # Ensure .gitkeep exists
        if (-not (Test-Path "data/backups/.gitkeep")) {
            New-Item "data/backups/.gitkeep" -ItemType File -Force | Out-Null
            Write-Host "✓ Created: data/backups/.gitkeep" -ForegroundColor Green
        }
    }
    
    Set-Location $rootPath
}

Write-Host "`n📂 Cleaning CA_Policy_Manager..." -ForegroundColor Yellow

# CA_Policy_Manager cleanup
if (Test-Path "CA_Policy_Manager") {
    Set-Location "CA_Policy_Manager"
    
    # CRITICAL: Remove config with credentials
    Remove-ItemSafely "config.json"
    
    # Remove backup and temporary files
    Remove-ItemSafely "ca_policy_examples_OLD.py.bak"
    Remove-ItemSafely "temp_script.js"
    Remove-ItemSafely "extract_js_data.py"
    Remove-ItemSafely "debug_report.py"
    Remove-ItemSafely "test_report_analyzer.py"
    Remove-ItemSafely "__pycache__" -Recurse
    
    Set-Location $rootPath
}

Write-Host "`n🔍 Searching for remaining sensitive files..." -ForegroundColor Yellow

# Search for potential secrets
$sensitivePatterns = @("*.env", "config.json", "*.secret", "*.key")
$foundSensitive = @()

foreach ($pattern in $sensitivePatterns) {
    $files = Get-ChildItem -Recurse -Filter $pattern -File -ErrorAction SilentlyContinue | 
             Where-Object { $_.Name -ne ".env.example" -and $_.Name -ne "config.json.template" }
    
    if ($files) {
        $foundSensitive += $files
        foreach ($file in $files) {
            Write-Host "⚠️  Found sensitive file: $($file.FullName)" -ForegroundColor Red
        }
    }
}

Write-Host "`n📊 Cleanup Summary" -ForegroundColor Cyan
Write-Host "==================" -ForegroundColor Cyan
Write-Host "Files deleted: $($deletedFiles.Count)" -ForegroundColor Green
Write-Host "Directories deleted: $($deletedDirs.Count)" -ForegroundColor Green

if ($errors.Count -gt 0) {
    Write-Host "`n⚠️  Errors encountered: $($errors.Count)" -ForegroundColor Yellow
    foreach ($error in $errors) {
        Write-Host "  - $error" -ForegroundColor Yellow
    }
}

if ($foundSensitive.Count -gt 0) {
    Write-Host "`n❌ CRITICAL: $($foundSensitive.Count) sensitive file(s) still exist!" -ForegroundColor Red
    Write-Host "Please review and remove these files before publishing:" -ForegroundColor Red
    foreach ($file in $foundSensitive) {
        Write-Host "  - $($file.FullName)" -ForegroundColor Red
    }
    Write-Host "`n⚠️  DO NOT PROCEED TO GITHUB UNTIL THESE ARE RESOLVED!" -ForegroundColor Red
} else {
    Write-Host "`n✅ No sensitive files detected!" -ForegroundColor Green
}

Write-Host "`n📋 Next Steps:" -ForegroundColor Cyan
Write-Host "1. Review GITHUB_PREP.md for complete checklist" -ForegroundColor White
Write-Host "2. Run: git status" -ForegroundColor White
Write-Host "3. Verify no sensitive files in git staging" -ForegroundColor White
Write-Host "4. Update README.md with your information" -ForegroundColor White
Write-Host "5. Test installation on clean machine" -ForegroundColor White
Write-Host "6. Create GitHub repository and push" -ForegroundColor White

Write-Host "`n🎉 Cleanup complete!`n" -ForegroundColor Green
