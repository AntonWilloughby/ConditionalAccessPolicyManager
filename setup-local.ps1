#!/usr/bin/env pwsh
# CA Policy Manager - Local Setup Script
# Run this script to quickly set up the app for local testing

Write-Host "🚀 CA Policy Manager - Local Setup" -ForegroundColor Green
Write-Host ""

# Check Python - Find real installation (not Windows Store stub)
Write-Host "1️⃣  Checking Python installation..." -ForegroundColor Cyan

# Find all Python executables
$pythonPaths = @(
    "python",
    "python3",
    "py",
    "C:\Program Files\Python311\python.exe",
    "C:\Program Files\Python312\python.exe",
    "$env:LOCALAPPDATA\Programs\Python\Python311\python.exe",
    "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe"
)

$pythonCmd = $null
$unsupportedVersions = @()

foreach ($pyPath in $pythonPaths) {
    try {
        $versionOutput = & $pyPath --version 2>&1
        if ($LASTEXITCODE -ne 0) { continue }

        if ($versionOutput -match 'Python (\d+\.\d+\.\d+)') {
            $versionParsed = [version]$Matches[1]
            if ($versionParsed.Major -eq 3 -and ($versionParsed.Minor -eq 11 -or $versionParsed.Minor -eq 12)) {
                $pythonCmd = $pyPath
                Write-Host "✅ Found supported Python $versionOutput at $pyPath" -ForegroundColor Green
                break
            }
            else {
                $unsupportedVersions += "$versionOutput at $pyPath"
            }
        }
    }
    catch { continue }
}

if (-not $pythonCmd) {
    if ($unsupportedVersions.Count -gt 0) {
        Write-Host "⚠️  Detected Python installations that are not supported by this tool:" -ForegroundColor Yellow
        $unsupportedVersions | ForEach-Object { Write-Host "   - $_" -ForegroundColor DarkYellow }
        Write-Host ""
    }

    Write-Host "❌ Python 3.11 or 3.12 not found!" -ForegroundColor Red
    Write-Host ""
    Write-Host "📥 Please install Python:" -ForegroundColor Yellow
    Write-Host "   1. Go to: https://www.python.org/downloads/" -ForegroundColor Cyan
    Write-Host "   2. Download Python 3.11 or 3.12" -ForegroundColor Cyan
    Write-Host "   3. During installation, check 'Add Python to PATH'" -ForegroundColor Cyan
    Write-Host "   4. Re-run this setup script" -ForegroundColor Cyan
    Write-Host ""
    pause
    exit 1
}

Write-Host ""

# Create virtual environment
Write-Host ""
Write-Host "2️⃣  Creating virtual environment..." -ForegroundColor Cyan
if (Test-Path .venv) {
    Write-Host "⚠️  Existing .venv found - cleaning..." -ForegroundColor Yellow
    Remove-Item .venv -Recurse -Force -ErrorAction SilentlyContinue
}

try {
    & $pythonCmd -m venv .venv
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Virtual environment created" -ForegroundColor Green
    }
    else {
        throw "venv creation failed"
    }
}
catch {
    Write-Host "❌ Failed to create virtual environment" -ForegroundColor Red
    Write-Host "   Error: $_" -ForegroundColor Yellow
    exit 1
}

Write-Host ""

# Activate virtual environment
Write-Host "3️⃣  Activating virtual environment..." -ForegroundColor Cyan
. .\.venv\Scripts\Activate.ps1
Write-Host "✅ Virtual environment activated" -ForegroundColor Green

Write-Host ""

# Install dependencies
Write-Host ""
Write-Host "4️⃣  Installing dependencies..." -ForegroundColor Cyan
cd CA_Policy_Manager_Web

Write-Host "   Upgrading pip..." -ForegroundColor Gray
pip install --upgrade pip setuptools wheel --quiet --disable-pip-version-check

Write-Host "   Installing packages (this may take 2-3 minutes)..." -ForegroundColor Gray
pip install -r requirements.txt --quiet --disable-pip-version-check

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ All dependencies installed successfully" -ForegroundColor Green
}
else {
    Write-Host "❌ Some packages failed to install" -ForegroundColor Red
    Write-Host "   Try running manually: pip install -r requirements.txt" -ForegroundColor Yellow
    exit 1
}

Write-Host ""

# Check for .env
Write-Host ""
Write-Host "5️⃣  Checking environment configuration..." -ForegroundColor Cyan
if (-not (Test-Path .env)) {
    Write-Host "⚠️  .env file not found" -ForegroundColor Yellow
    Write-Host "   Creating from template..." -ForegroundColor Yellow
    
    # Generate SECRET_KEY automatically
    $secretKey = & $pythonCmd -c "import secrets; print(secrets.token_hex(32))"
    
    # Read template and replace SECRET_KEY and enable DEMO_MODE
    $envContent = Get-Content .env.example -Raw
    $envContent = $envContent -replace 'SECRET_KEY=.*', "SECRET_KEY=$secretKey"
    $envContent = $envContent -replace '#DEMO_MODE=.*', "DEMO_MODE=true"
    $envContent | Set-Content .env
    
    Write-Host "✅ .env file created with auto-generated SECRET_KEY" -ForegroundColor Green
    Write-Host "✅ DEMO_MODE enabled - app will run without Azure credentials" -ForegroundColor Green
    Write-Host ""
    Write-Host "📝 OPTIONAL: For full functionality, edit .env and set:" -ForegroundColor Cyan
    Write-Host "   - MSAL_CLIENT_ID (from Azure App Registration)" -ForegroundColor Gray
    Write-Host "   - MSAL_CLIENT_SECRET (optional unless you use client-credential auth)" -ForegroundColor Gray
    Write-Host "   - Set DEMO_MODE=false" -ForegroundColor Gray
    Write-Host ""
    Write-Host "   See docs/QUICK_SETUP.md for Azure setup instructions" -ForegroundColor Gray
}
else {
    Write-Host "✅ .env file exists" -ForegroundColor Green
    
    # Check if critical values are set
    $envContent = Get-Content .env -Raw
    $demoModeMatch = [regex]::Match($envContent, 'DEMO_MODE\s*=\s*(\w+)')
    $demoModeEnabled = $demoModeMatch.Success -and $demoModeMatch.Groups[1].Value.ToLower() -eq 'true'

    $clientIdSet = $envContent -match 'MSAL_CLIENT_ID=(?!your_)\S+'
    $clientSecretPlaceholder = $envContent -match 'MSAL_CLIENT_SECRET=(?:your_|$)'

    if (-not $clientIdSet) {
        if ($demoModeEnabled) {
            Write-Host "ℹ️  MSAL_CLIENT_ID is still a placeholder. Demo mode is enabled, so sign-in is disabled until you set a real client ID." -ForegroundColor Yellow
        }
        else {
            Write-Host "❗ MSAL_CLIENT_ID is missing but DEMO_MODE=false. Authentication will fail until you set a real client ID." -ForegroundColor Red
        }
    }

    if ($clientSecretPlaceholder) {
        Write-Host "ℹ️  MSAL_CLIENT_SECRET is still a placeholder. This is optional for delegated sign-in but required for client credential flows." -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "=" * 60 -ForegroundColor Green
Write-Host "✅ Setup complete!" -ForegroundColor Green
Write-Host "=" * 60 -ForegroundColor Green

Write-Host ""
Write-Host "🚀 To start the app, run:" -ForegroundColor Cyan
Write-Host "   python app.py" -ForegroundColor Yellow

Write-Host ""
Write-Host "🌐 Then open in browser:" -ForegroundColor Cyan
Write-Host "   http://localhost:5000" -ForegroundColor Yellow

Write-Host ""
Write-Host "📚 For more details, see:" -ForegroundColor Cyan
Write-Host "   ../LOCAL_TESTING_GUIDE.md" -ForegroundColor Yellow

Write-Host ""
Write-Host "🔁 If you change values in .env later (especially DEMO_MODE), fully stop running python processes so Flask reloads the new environment." -ForegroundColor Cyan
Write-Host "   Example: Stop-Process -Name python -Force" -ForegroundColor Gray
Write-Host ""
