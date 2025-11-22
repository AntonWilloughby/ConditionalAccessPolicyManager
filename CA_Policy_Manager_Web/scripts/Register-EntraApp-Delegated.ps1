# Quick App Registration for CA Policy Manager
# This script creates an Azure AD app with DELEGATED permissions only
# No admin consent needed - users consent when they first sign in!

Write-Host "🚀 CA Policy Manager - Quick Setup" -ForegroundColor Cyan
Write-Host ""

# Check if connected to Azure
$context = Get-AzContext -ErrorAction SilentlyContinue
if (-not $context) {
    Write-Host "Connecting to Azure..." -ForegroundColor Yellow
    Connect-AzAccount
}

$tenantId = $context.Tenant.Id
Write-Host "✅ Connected to tenant: $tenantId" -ForegroundColor Green
Write-Host ""

# App details
$appName = "CA Policy Manager"
$redirectUri = "http://localhost:5000/auth/callback"

Write-Host "Creating app registration..." -ForegroundColor Yellow
Write-Host "  Name: $appName" -ForegroundColor Gray
Write-Host "  Redirect URI: $redirectUri" -ForegroundColor Gray
Write-Host ""

# Check if app already exists
$existingApp = Get-AzADApplication -DisplayName $appName -ErrorAction SilentlyContinue

if ($existingApp) {
    Write-Host "⚠️  App already exists!" -ForegroundColor Yellow
    Write-Host "   App ID: $($existingApp.AppId)" -ForegroundColor Cyan
    $continue = Read-Host "Delete and recreate? (y/N)"
    
    if ($continue -eq 'y') {
        Remove-AzADApplication -ObjectId $existingApp.Id
        Write-Host "🗑️  Deleted existing app" -ForegroundColor Yellow
    } else {
        Write-Host "Using existing app..." -ForegroundColor Green
        $app = $existingApp
    }
}

if (-not $existingApp -or $continue -eq 'y') {
    # Create the app
    $app = New-AzADApplication -DisplayName $appName -WebRedirectUri $redirectUri
    Write-Host "✅ App created!" -ForegroundColor Green
}

$appId = $app.AppId

# Microsoft Graph App ID
$graphAppId = "00000003-0000-0000-c000-000000000000"

# Delegated permissions (no admin consent required for most)
$delegatedPermissions = @{
    "Policy.Read.All" = "37f7f235-527c-4136-accd-4a02d197296e"
    "Policy.ReadWrite.ConditionalAccess" = "ad902697-1014-4ef5-81ef-2b4301988e8c"
    "Application.Read.All" = "c79f8feb-a9db-4090-85f9-90d820caa0eb"
    "Directory.Read.All" = "06da0dbc-49e2-44d2-8312-53f166ab848a"
    "Group.ReadWrite.All" = "4e46008b-f24c-477d-8fff-7bb4ec7aafe0"
    "User.Read" = "e1fe6dd8-ba31-4d61-89e7-88639da4683d"
}

Write-Host "Adding permissions..." -ForegroundColor Yellow

# Build resource access array
$resourceAccess = @()
foreach ($permName in $delegatedPermissions.Keys) {
    $resourceAccess += @{
        Id = $delegatedPermissions[$permName]
        Type = "Scope"  # Delegated permission
    }
    Write-Host "  ✓ $permName (Delegated)" -ForegroundColor Green
}

# Apply permissions
$graphResource = @{
    ResourceAppId = $graphAppId
    ResourceAccess = $resourceAccess
}

Update-AzADApplication -ObjectId $app.Id -RequiredResourceAccess @($graphResource)

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "✅ Setup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "📋 App Details:" -ForegroundColor Cyan
Write-Host "  App Name: $appName" -ForegroundColor White
Write-Host "  Client ID: $appId" -ForegroundColor White
Write-Host "  Tenant ID: $tenantId" -ForegroundColor White
Write-Host "  Redirect URI: $redirectUri" -ForegroundColor White
Write-Host ""
Write-Host "🔐 Permissions (Delegated - User Consent):" -ForegroundColor Cyan
foreach ($permName in $delegatedPermissions.Keys) {
    Write-Host "  • $permName" -ForegroundColor White
}
Write-Host ""
Write-Host "📝 Next Steps:" -ForegroundColor Yellow
Write-Host "  1. Copy your Client ID: $appId" -ForegroundColor White
Write-Host "  2. Update MSAL_CLIENT_ID in app.py (or set environment variable)" -ForegroundColor White
Write-Host "  3. Restart the web application" -ForegroundColor White
Write-Host "  4. Sign in - you'll be prompted to consent to permissions" -ForegroundColor White
Write-Host ""
Write-Host "💡 Tips:" -ForegroundColor Cyan
Write-Host "  • Delegated permissions don't require admin consent" -ForegroundColor Gray
Write-Host "  • Users will see a consent screen on first sign-in" -ForegroundColor Gray
Write-Host "  • Some permissions (like Group.ReadWrite.All) may need admin approval" -ForegroundColor Gray
Write-Host ""
Write-Host "🌐 Azure Portal Link:" -ForegroundColor Cyan
Write-Host "  https://portal.azure.com/#view/Microsoft_AAD_RegisteredApps/ApplicationMenuBlade/Overview/appId/$appId" -ForegroundColor Blue
Write-Host ""

# Offer to update app.py
$updateApp = Read-Host "Update app.py with this Client ID? (Y/n)"

if ($updateApp -ne 'n') {
    $appPyPath = Join-Path $PSScriptRoot "..\app.py"
    
    if (Test-Path $appPyPath) {
        $content = Get-Content $appPyPath -Raw
        
        # Update the MSAL_CLIENT_ID line
        $pattern = "MSAL_CLIENT_ID = os\.environ\.get\('MSAL_CLIENT_ID', '[^']*'\)"
        $replacement = "MSAL_CLIENT_ID = os.environ.get('MSAL_CLIENT_ID', '$appId')"
        
        if ($content -match $pattern) {
            $content = $content -replace $pattern, $replacement
            Set-Content -Path $appPyPath -Value $content -NoNewline
            Write-Host "✅ app.py updated with Client ID!" -ForegroundColor Green
        } else {
            Write-Host "⚠️  Could not find MSAL_CLIENT_ID pattern in app.py" -ForegroundColor Yellow
            Write-Host "   Please manually update: MSAL_CLIENT_ID = '$appId'" -ForegroundColor Gray
        }
    } else {
        Write-Host "⚠️  Could not find app.py at: $appPyPath" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "🎉 All done! Start your app and sign in." -ForegroundColor Green
Write-Host ""
