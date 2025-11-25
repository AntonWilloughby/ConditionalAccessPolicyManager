#!/usr/bin/env pwsh
# Diagnostic Script - Run this if you're having setup issues
# This will check your environment and help identify problems

Write-Host ""
Write-Host "🔍 CA Policy Manager - Environment Diagnostic" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""

$issues = @()
$warnings = @()

# Check 1: Python Installation
Write-Host "1️⃣  Checking Python Installation..." -ForegroundColor Yellow
try {
    $pythonPaths = @(
        "python",
        "python3",
        "py",
        "C:\Program Files\Python311\python.exe",
        "C:\Program Files\Python312\python.exe",
        "$env:LOCALAPPDATA\Programs\Python\Python311\python.exe",
        "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe"
    )
    
    $pythonFound = $false
    foreach ($pyPath in $pythonPaths) {
        try {
            $version = & $pyPath --version 2>&1
            if ($LASTEXITCODE -eq 0 -and $version -match 'Python (3\.(1[1-9]|[2-9]\d))') {
                Write-Host "   ✅ Python found: $version at $pyPath" -ForegroundColor Green
                $pythonFound = $true
                
                # Check if it's Windows Store stub
                $fullPath = (Get-Command $pyPath -ErrorAction SilentlyContinue).Source
                if ($fullPath -match "WindowsApps") {
                    $warnings += "Python is Windows Store version - may cause issues. Recommend installing from python.org"
                }
                break
            }
        }
        catch { continue }
    }
    
    if (-not $pythonFound) {
        Write-Host "   ❌ Python 3.11+ not found" -ForegroundColor Red
        $issues += "Python 3.11+ not installed or not in PATH"
    }
}
catch {
    Write-Host "   ❌ Error checking Python: $_" -ForegroundColor Red
    $issues += "Python check failed: $_"
}

Write-Host ""

# Check 2: Virtual Environment
Write-Host "2️⃣  Checking Virtual Environment..." -ForegroundColor Yellow
if (Test-Path .venv) {
    Write-Host "   ✅ .venv directory exists" -ForegroundColor Green
    
    # Check if Python executable exists in venv
    $venvPython = ".venv\Scripts\python.exe"
    if (Test-Path $venvPython) {
        Write-Host "   ✅ Python executable found in venv" -ForegroundColor Green
        
        # Try to get version from venv
        try {
            $venvVersion = & $venvPython --version 2>&1
            if ($LASTEXITCODE -eq 0) {
                Write-Host "   ✅ venv Python version: $venvVersion" -ForegroundColor Green
            }
            else {
                Write-Host "   ⚠️  venv Python not working properly" -ForegroundColor Yellow
                $warnings += "Virtual environment Python may be broken - try recreating"
            }
        }
        catch {
            Write-Host "   ⚠️  Cannot execute venv Python" -ForegroundColor Yellow
            $warnings += "Virtual environment may need to be recreated"
        }
    }
    else {
        Write-Host "   ❌ Python.exe not found in venv" -ForegroundColor Red
        $issues += "Virtual environment appears incomplete"
    }
}
else {
    Write-Host "   ⚠️  No virtual environment found" -ForegroundColor Yellow
    $warnings += "Virtual environment not created - run setup script"
}

Write-Host ""

# Check 3: Dependencies
Write-Host "3️⃣  Checking Python Packages..." -ForegroundColor Yellow
if (Test-Path .venv) {
    $venvPython = ".venv\Scripts\python.exe"
    if (Test-Path $venvPython) {
        try {
            $packages = & $venvPython -m pip list --format=freeze 2>&1
            $requiredPackages = @("flask", "msal", "redis", "flask-wtf", "flask-session")
            
            foreach ($pkg in $requiredPackages) {
                if ($packages -match "^$pkg==") {
                    $version = ($packages | Select-String "^$pkg==").Line
                    Write-Host "   ✅ $version" -ForegroundColor Green
                }
                else {
                    Write-Host "   ❌ $pkg not installed" -ForegroundColor Red
                    $issues += "$pkg package not installed"
                }
            }
        }
        catch {
            Write-Host "   ⚠️  Cannot check packages: $_" -ForegroundColor Yellow
            $warnings += "Unable to verify installed packages"
        }
    }
}
else {
    Write-Host "   ⚠️  Skipped (no venv)" -ForegroundColor Yellow
}

Write-Host ""

# Check 4: Configuration Files
Write-Host "4️⃣  Checking Configuration Files..." -ForegroundColor Yellow

# Check .env.example
if (Test-Path "CA_Policy_Manager_Web\.env.example") {
    Write-Host "   ✅ .env.example exists" -ForegroundColor Green
}
else {
    Write-Host "   ❌ .env.example not found" -ForegroundColor Red
    $issues += ".env.example template missing"
}

# Check .env
if (Test-Path "CA_Policy_Manager_Web\.env") {
    Write-Host "   ✅ .env file exists" -ForegroundColor Green
    
    # Check if .env has required values
    $envContent = Get-Content "CA_Policy_Manager_Web\.env" -Raw
    
    if ($envContent -match 'MSAL_CLIENT_ID=(?!your_)\S+') {
        Write-Host "   ✅ MSAL_CLIENT_ID is set" -ForegroundColor Green
    }
    else {
        Write-Host "   ⚠️  MSAL_CLIENT_ID not configured" -ForegroundColor Yellow
        $warnings += "MSAL_CLIENT_ID needs to be set in .env"
    }
    
    if ($envContent -match 'MSAL_CLIENT_SECRET=(?!your_)\S+') {
        Write-Host "   ✅ MSAL_CLIENT_SECRET is set" -ForegroundColor Green
    }
    else {
        Write-Host "   ⚠️  MSAL_CLIENT_SECRET not configured" -ForegroundColor Yellow
        $warnings += "MSAL_CLIENT_SECRET needs to be set in .env"
    }
    
    if ($envContent -match 'SECRET_KEY=\S{32,}') {
        Write-Host "   ✅ SECRET_KEY is set" -ForegroundColor Green
    }
    else {
        Write-Host "   ⚠️  SECRET_KEY may not be secure" -ForegroundColor Yellow
        $warnings += "SECRET_KEY should be regenerated"
    }
}
else {
    Write-Host "   ⚠️  .env file not found" -ForegroundColor Yellow
    $warnings += ".env file needs to be created - run setup script"
}

Write-Host ""

# Check 5: Required Files
Write-Host "5️⃣  Checking Required Application Files..." -ForegroundColor Yellow
$requiredFiles = @(
    "CA_Policy_Manager_Web\app.py",
    "CA_Policy_Manager_Web\config.py",
    "CA_Policy_Manager_Web\session_manager.py",
    "CA_Policy_Manager_Web\requirements.txt"
)

foreach ($file in $requiredFiles) {
    if (Test-Path $file) {
        Write-Host "   ✅ $file exists" -ForegroundColor Green
    }
    else {
        Write-Host "   ❌ $file missing" -ForegroundColor Red
        $issues += "Required file missing: $file"
    }
}

Write-Host ""

# Check 6: Network & Ports
Write-Host "6️⃣  Checking Network Configuration..." -ForegroundColor Yellow

# Check if port 5000 is available
try {
    $portCheck = Get-NetTCPConnection -LocalPort 5000 -State Listen -ErrorAction SilentlyContinue
    if ($portCheck) {
        Write-Host "   ⚠️  Port 5000 is already in use" -ForegroundColor Yellow
        $warnings += "Port 5000 in use - you may need to use a different port"
    }
    else {
        Write-Host "   ✅ Port 5000 is available" -ForegroundColor Green
    }
}
catch {
    Write-Host "   ⚠️  Cannot check port status" -ForegroundColor Yellow
}

# Check internet connectivity
try {
    $testConnection = Test-Connection -ComputerName "graph.microsoft.com" -Count 1 -Quiet -ErrorAction SilentlyContinue
    if ($testConnection) {
        Write-Host "   ✅ Internet connectivity OK" -ForegroundColor Green
    }
    else {
        Write-Host "   ⚠️  Cannot reach graph.microsoft.com" -ForegroundColor Yellow
        $warnings += "Internet connectivity issue - required for Microsoft Graph API"
    }
}
catch {
    Write-Host "   ⚠️  Cannot test connectivity" -ForegroundColor Yellow
}

Write-Host ""

# Check 7: Security Fixes
Write-Host "7️⃣  Checking Security Fixes..." -ForegroundColor Yellow
if (Test-Path "validate-security-fixes.ps1") {
    Write-Host "   ✅ Security validation script exists" -ForegroundColor Green
    Write-Host "   ℹ️  Run .\validate-security-fixes.ps1 to verify security" -ForegroundColor Cyan
}
else {
    Write-Host "   ⚠️  Security validation script not found" -ForegroundColor Yellow
    $warnings += "Missing security validation script"
}

Write-Host ""
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "📊 Diagnostic Summary" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""

if ($issues.Count -eq 0 -and $warnings.Count -eq 0) {
    Write-Host "✅ All checks passed! Your environment looks good." -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Cyan
    Write-Host "  1. Make sure .env has your Azure credentials" -ForegroundColor Gray
    Write-Host "  2. Run: cd CA_Policy_Manager_Web; python app.py" -ForegroundColor Gray
    Write-Host "  3. Open: http://localhost:5000" -ForegroundColor Gray
}
else {
    if ($issues.Count -gt 0) {
        Write-Host "❌ Critical Issues Found ($($issues.Count)):" -ForegroundColor Red
        foreach ($issue in $issues) {
            Write-Host "   • $issue" -ForegroundColor Red
        }
        Write-Host ""
    }
    
    if ($warnings.Count -gt 0) {
        Write-Host "⚠️  Warnings ($($warnings.Count)):" -ForegroundColor Yellow
        foreach ($warning in $warnings) {
            Write-Host "   • $warning" -ForegroundColor Yellow
        }
        Write-Host ""
    }
    
    Write-Host "🔧 Recommended Actions:" -ForegroundColor Cyan
    
    if ($issues -match "Python") {
        Write-Host "  1. Install Python 3.11+ from https://python.org/downloads/" -ForegroundColor Gray
        Write-Host "     During install, check 'Add Python to PATH'" -ForegroundColor Gray
    }
    
    if ($issues -match "Virtual environment" -or $warnings -match "venv") {
        Write-Host "  2. Recreate virtual environment:" -ForegroundColor Gray
        Write-Host "     Remove-Item .venv -Recurse -Force" -ForegroundColor Gray
        Write-Host "     .\setup-local.ps1" -ForegroundColor Gray
    }
    
    if ($issues -match "package" -or $warnings -match "package") {
        Write-Host "  3. Reinstall dependencies:" -ForegroundColor Gray
        Write-Host "     cd CA_Policy_Manager_Web" -ForegroundColor Gray
        Write-Host "     pip install -r requirements.txt" -ForegroundColor Gray
    }
    
    if ($warnings -match "MSAL") {
        Write-Host "  4. Configure Azure credentials in .env file" -ForegroundColor Gray
        Write-Host "     See: docs\QUICK_SETUP.md for instructions" -ForegroundColor Gray
    }
    
    if ($warnings -match "Port 5000") {
        Write-Host "  5. Use different port:" -ForegroundColor Gray
        Write-Host "     `$env:PORT=`"5001`"; python app.py" -ForegroundColor Gray
    }
}

Write-Host ""
Write-Host "📚 Additional Help:" -ForegroundColor Cyan
Write-Host "   • FIRST_TIME_SETUP_CHECKLIST.md - Complete setup guide" -ForegroundColor Gray
Write-Host "   • LOCAL_TESTING_GUIDE.md - Detailed troubleshooting" -ForegroundColor Gray
Write-Host "   • QUICK_START.md - Quick start guide" -ForegroundColor Gray
Write-Host ""
